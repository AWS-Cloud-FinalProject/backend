from datetime import datetime, timedelta, date
import jwt
import os
from fastapi import HTTPException, Header
from routers.cognito import verify_cognito_token

def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(data, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))


def verify_token(access_token: str = Header(None)):
    """Cognito 토큰 검증 함수"""
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token is missing")
    
    user = verify_cognito_token(access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user

def string_to_date(date_int: int):
    # 문자열을 "YYYY-MM-DD" 형식으로 변환'
    date_str = str(date_int)
    formatted_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    
    return formatted_str