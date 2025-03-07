<<<<<<< HEAD
from datetime import datetime, timedelta
=======
from datetime import datetime, timedelta, date
>>>>>>> 971cf4c0f5d5161873f3d6b4f8a6aec35995edd8
import jwt
import os
from fastapi import HTTPException, Header

def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(data, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))


def verify_token(access_token: str = Header(None)):
    """JWT 토큰 검증 함수 (헤더에서 access-token 키 사용)"""
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token is missing")
    try:
        payload = jwt.decode(access_token, os.getenv('SECRET_KEY'), algorithms=os.getenv('ALGORITHM'))
        return payload  # payload에 저장된 사용자 정보 반환
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
<<<<<<< HEAD
        raise HTTPException(status_code=401, detail="Invalid token")
=======
        raise HTTPException(status_code=401, detail="Invalid token")
        
def string_to_date(date_int: int):
    # 문자열을 "YYYY-MM-DD" 형식으로 변환'
    date_str = str(date_int)
    formatted_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    
    return formatted_str
>>>>>>> 971cf4c0f5d5161873f3d6b4f8a6aec35995edd8
