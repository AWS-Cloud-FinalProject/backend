from fastapi import FastAPI, HTTPException, Header
from routers import user, todo, diary
from dotenv import load_dotenv
from routers.cognito import cognito_client, CLIENT_ID

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
        response = cognito_client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token
            }
        )
        
        return {
            "access_token": response['AuthenticationResult']['AccessToken']
        }
    except Exception as e:
        raise HTTPException(status_code=403, detail="Invalid Refresh Token")

# Routers
app.include_router(user.router)
app.include_router(todo.router)
app.include_router(diary.router)