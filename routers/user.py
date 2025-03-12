from fastapi import APIRouter, HTTPException, Depends
from models import SignUp, SignIn, WithDraw, EditPW
from database import get_db_connection
from routers.cognito import cognito_client, CLIENT_ID, USER_POOL_ID
from functions import verify_token
import bcrypt
from dotenv import load_dotenv
from functions import create_jwt_token
import os
import boto3

load_dotenv()

# 환경변수 확인을 위한 디버그 출력
print("Region:", os.getenv('AWS_REGION'))
print("User Pool ID:", os.getenv('COGNITO_USER_POOL_ID'))
print("Client ID:", os.getenv('COGNITO_CLIENT_ID'))

# Cognito 클라이언트 설정
cognito_client = boto3.client('cognito-idp',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

# 상수 정의
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')

if not USER_POOL_ID or not CLIENT_ID:
    raise ValueError("Cognito environment variables are not properly set")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

router = APIRouter()

# @router.get("/protected")
# def protected_route(token: str = Depends(verify_token)):
#     """보호된 API 엔드포인트"""
#     return {"message": "Access granted", "user": token["sub"]}

# 회원가입
@router.post("/sign-up")
def create_user(user: SignUp):
    try:
        # Cognito에 사용자 생성
        cognito_response = cognito_client.sign_up(
            ClientId=CLIENT_ID,
            Username=user.id,
            Password=user.password,
            UserAttributes=[
                {
                    'Name': 'name',
                    'Value': user.name
                },
                {
                    'Name': 'email',
                    'Value': user.email
                }
            ]
        )
        
        # 사용자 자동 확인 (이메일 인증 없이)
        cognito_client.admin_confirm_sign_up(
            UserPoolId=USER_POOL_ID,
            Username=user.id
        )
        
        # DB에 사용자 정보 저장
        db = get_db_connection()
        hashed_password = hash_password(user.password)
        with db.cursor() as cursor:
            sql = "INSERT INTO USER (id, name, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (user.id, user.name, hashed_password))
            db.commit()
        db.close()
        
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 로그인
@router.post("/sign-in")
def sign_in(user: SignIn):
    try:
        # Cognito로 인증
        auth_response = cognito_client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': user.id,
                'PASSWORD': user.password
            }
        )
        
        return {
            "access_token": auth_response['AuthenticationResult']['AccessToken'],
            "refresh_token": auth_response['AuthenticationResult']['RefreshToken'],
            "id_token": auth_response['AuthenticationResult']['IdToken']
        }
    except Exception as e:
        raise HTTPException(status_code=403, detail="LoginError")

# 회원 탈퇴
@router.delete("/withdraw")
def withdraw(user: WithDraw, token: dict = Depends(verify_token)):
    try:
        username = token["username"]
        
        # 현재 비밀번호 확인
        try:
            cognito_client.initiate_auth(
                ClientId=CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': user.password
                }
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        # 비밀번호가 확인되면 사용자 삭제 진행
        cognito_client.admin_delete_user(
            UserPoolId=USER_POOL_ID,
            Username=username
        )
        
        # DB에서도 사용자 삭제
        db = get_db_connection()
        with db.cursor() as cursor:
            sql = "DELETE FROM USER WHERE id = %s"
            cursor.execute(sql, (username,))
            db.commit()
        db.close()
        
        return {"message": "User Withdraw Success"}
    except Exception as e:
        print(f"Withdraw error: {str(e)}")
        if "Current password is incorrect" in str(e):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        raise HTTPException(status_code=400, detail=str(e))

# 비밀번호 변경
@router.patch("/edit-pw")
def edit_pw(user: EditPW, token: dict = Depends(verify_token)):
    try:
        username = token["username"]
        
        # 기존 비밀번호 확인
        try:
            cognito_client.initiate_auth(
                ClientId=CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': user.password
                }
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        # 비밀번호 변경
        cognito_client.admin_set_user_password(
            UserPoolId=USER_POOL_ID,
            Username=username,
            Password=user.new_password,
            Permanent=True
        )
        
        # DB 업데이트 (필요한 경우)
        db = get_db_connection()
        with db.cursor() as cursor:
            sql = "UPDATE USER SET password = %s WHERE id = %s"
            cursor.execute(sql, (user.new_password, username))
            db.commit()
        db.close()
        
        return {"message": "Password updated successfully"}
    except Exception as e:
        print(f"Password update error: {str(e)}")
        if "Current password is incorrect" in str(e):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        raise HTTPException(status_code=400, detail=str(e))