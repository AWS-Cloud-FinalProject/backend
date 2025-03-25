from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from routers import user, todo, diary, community
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from routers.cognito import cognito_client, CLIENT_ID
from prometheus_fastapi_instrumentator import Instrumentator

load_dotenv()

app = FastAPI()  # API 경로 접두어 설정

# CORS 미들웨어 설정
origins = [
    "http://wiary.site",  # 허용할 출처 목록을 여기에 추가
]


# 미들웨어로 X-Requested-With 헤더 체크
class RedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # /health 경로를 제외하고 리디렉션을 적용하도록 수정
        if request.url.path != "/health" and request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return RedirectResponse(url='/')  # 리디렉트 주소 수정
        response = await call_next(request)
        return response


# 미들웨어 순서를 수정하여 RedirectMiddleware가 먼저 실행되도록 설정
app.add_middleware(RedirectMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PATCH"],
    allow_headers=["*"],
)


# API 경로에서 '/api' 접두어를 제거하는 미들웨어
@app.middleware("http")
async def add_api_prefix(request: Request, call_next):
    # 'x-forwarded-prefix' 헤더에서 접두어를 가져옴
    prefix = request.headers.get("x-forwarded-prefix", "/api")
    # 경로에서 접두어를 제거
    request.scope["path"] = request.scope["path"].removeprefix(prefix)
    response = await call_next(request)
    return response


# Prometheus 메트릭 설정 (기본 설정만 사용)
instrumentator = Instrumentator().instrument(app)


@app.on_event("startup")
async def startup():
    # 기본 설정으로 Prometheus 메트릭 활성화
    instrumentator.expose(app, endpoint="/metrics")


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


@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Service is running"}


# Routers
app.include_router(user.router, tags=["User"])
app.include_router(todo.router, tags=["Todo"])
app.include_router(diary.router, tags=["Diary"])
app.include_router(community.router, tags=["Community"])