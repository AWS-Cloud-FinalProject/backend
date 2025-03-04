from fastapi import FastAPI
from models import User
from database import get_db_connection
from functions import hash_password, verify_password

app = FastAPI()
'''
1. 유저
2. 일기
3. 투두
'''


@app.get("/ping")
def ping():
    return "pong"

# 회원가입
@app.post("/sign-up")
def create_user(user: User):
    db = get_db_connection()
    hashed_password = hash_password(user.password)
    with db.cursor() as cursor:
        cursor.execute(f"INSERT INTO USER (id, name, password) VALUES ({user.id}, {user.name}, {hashed_password})")
        db.commit()
    db.close()
    return {"message": "User created successfully"}