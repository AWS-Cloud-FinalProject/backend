import datetime
import jwt
import os
from fastapi import HTTPException, Header

def create_jwt_token(data: dict, expires_delta: int = 60):
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    data.update({"exp": expire})
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
        raise HTTPException(status_code=401, detail="Invalid token")