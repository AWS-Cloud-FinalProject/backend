from fastapi import FastAPI
from routers import user

app = FastAPI()
'''
1. 유저
2. 일기
3. 투두
'''

@app.get("/ping")
def ping():
    return "pong"

app.include_router(user.router)