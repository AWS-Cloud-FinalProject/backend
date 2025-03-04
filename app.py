from fastapi import FastAPI
from routers import user, todo

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

app.include_router(user.router)
app.include_router(todo.router)