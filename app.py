from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from routers import user, todo, diary, community_post
from dotenv import load_dotenv
from routers.cognito import cognito_client, CLIENT_ID

load_dotenv()

app = FastAPI()

origins = [
    "http://wiary.site",  # 프론트엔드 도메인만 허용
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 출처 목록
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PATCH"],  # 허용할 HTTP 메서드
    allow_headers=["*"],  # 모든 헤더 허용
)

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

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Service is running"}

# Routers
app.include_router(user.router, tags=["User"])
app.include_router(todo.router, tags=["Todo"])
app.include_router(diary.router, tags=["Diary"])
app.include_router(community_post.router, tags=["Community Post"])