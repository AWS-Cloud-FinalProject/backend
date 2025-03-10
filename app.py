import os
from datetime import timedelta
from fastapi import FastAPI, HTTPException, Header
from routers import user, todo, diary
from functions import create_jwt_token
import jwt
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
'''
1. 유저
2. 일기
3. 투두
'''

# 서버 상태 확인
@app.get("/ping")
def ping():
    return "pongggggggggggg"

@app.post("/refresh-token")
def refresh_access_token(refresh_token: str = Header(None)):
    """
    Access Token 만료 시 Refresh Token으로 Access Token 발급 받는 API
    """
    if not refresh_token:
        raise HTTPException(status_code=403, detail="Refresh Token required")
    try:
        payload = jwt.decode(refresh_token, os.getenv('SECRET_KEY'), algorithms=os.getenv('ALGORITHM'))
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=403, detail="Invalid Refresh Token")

        # 새로운 Access Token 발급
        new_access_token = create_jwt_token({"sub": user_id}, timedelta(minutes=180))
        return {"access_token": new_access_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Refresh Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid Refresh Token")

# Routers
app.include_router(user.router)
app.include_router(todo.router)
app.include_router(diary.router)
