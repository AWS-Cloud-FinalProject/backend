from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from routers import user, todo, diary, community
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from routers.cognito import cognito_client, CLIENT_ID
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import time
import re

load_dotenv()

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

app = FastAPI()  # API 경로 접두어 설정

# Prometheus 메트릭 설정 (기본 설정만 사용)
# 미들웨어 추가 전에 instrumentator 초기화
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/metrics")

# CORS 미들웨어 설정
origins = [
    "http://wiary.site",  # 허용할 출처 목록을 여기에 추가
]


# 미들웨어로 X-Requested-With 헤더 체크
class RedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # /health와 /metrics 경로를 제외하고 리디렉션을 적용하도록 수정
        if request.url.path not in ["/health", "/metrics"] and request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return RedirectResponse(url='/')  # 리디렉트 주소 수정
        response = await call_next(request)
        return response


# 로깅 미들웨어 정의
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 기본 요청 정보 수집
        method = request.method
        path = request.url.path
        
        # 클라이언트 IP 주소 가져오기
        forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = forwarded_for.split(",")[0] if forwarded_for else request.client.host
        
        # 민감 정보 필터링 (예: 토큰, 비밀번호)
        query_params = str(request.query_params)
        query_params = re.sub(r'(token|password|secret)=([^&]*)', r'\1=***', query_params)
        
        # 헬스체크와 메트릭스는 DEBUG 레벨로, 나머지는 INFO 레벨로 로깅
        if path in ["/health", "/metrics"]:
            logger.debug(f"Request: {method} {path} - Client: {client_ip} - Params: {query_params}")
        else:
            logger.info(f"Request: {method} {path} - Client: {client_ip} - Params: {query_params}")
        
        # 요청 처리
        response = await call_next(request)
        
        # 응답 시간 계산
        process_time = time.time() - start_time
        status_code = response.status_code
        
        # 상태 코드에 따라 로깅 레벨 조정 (헬스체크와 메트릭스는 항상 DEBUG)
        if path in ["/health", "/metrics"]:
            logger.debug(f"Response: {method} {path} - Status: {status_code} - Time: {process_time:.4f}s")
        elif 200 <= status_code < 400:
            logger.info(f"Response: {method} {path} - Status: {status_code} - Time: {process_time:.4f}s")
        else:
            logger.warning(f"Response: {method} {path} - Status: {status_code} - Time: {process_time:.4f}s")
        
        return response


# 미들웨어 순서 변경: 로깅 미들웨어를 먼저 등록하여 모든 요청이 로깅되도록 함
app.add_middleware(LoggingMiddleware)  # 먼저 로깅
app.add_middleware(RedirectMiddleware)  # 그 다음 리디렉션
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