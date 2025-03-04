from fastapi import APIRouter, HTTPException
from models import SignUp, UserAccount, EditPW
from database import get_db_connection
import bcrypt
from dotenv import load_dotenv
from functions import create_jwt_token

load_dotenv()


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
    db = get_db_connection()
    hashed_password = hash_password(user.password)
    with db.cursor() as cursor:
        sql = "INSERT INTO USER (id, name, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (user.id, user.name, hashed_password))
        db.commit()
    db.close()
    return {"message": "User created successfully"}

# 로그인
@router.post("/sign-in")
def sign_in(user: UserAccount):
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "SELECT password FROM USER WHERE id = %s"
        cursor.execute(sql, (user.id))
        hashed_password = cursor.fetchone()['password']
        verified_password = verify_password(user.password, hashed_password)
        if verified_password:
            token = create_jwt_token({"sub": user.id})
            return {"access_token": token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=403, detail="LoginError")

# 회원 탈퇴
@router.delete("/withdraw")
def withdraw(user: UserAccount):
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "SELECT password FROM USER WHERE id = %s"
        cursor.execute(sql, (user.id))
        hashed_password = cursor.fetchone()['password']
        verified_password = verify_password(user.password, hashed_password)
        if verified_password:
            sql = "DELETE FROM USER WHERE id = %s"
            cursor.execute(sql, (user.id))
            db.commit()
            return {"message": "User Withdraw Success"}
        else:
            raise HTTPException(status_code=403, detail="WithDrawError")

# 비밀번호 변경
@router.patch("/edit-pw")
def edit_pw(user: EditPW):
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "SELECT password FROM USER WHERE id = %s"
        cursor.execute(sql, (user.id))
        hashed_password = cursor.fetchone()['password']
        verified_password = verify_password(user.password, hashed_password)
        if verified_password:
            new_hashed_password = hash_password(user.new_password)
            sql = "UPDATE USER SET password = %s WHERE id = %s"
            cursor.execute(sql, (new_hashed_password, user.id))
            db.commit()
            return {"message": "User password updated successfully"}
        else:
            raise HTTPException(status_code=403, detail="PasswordError")