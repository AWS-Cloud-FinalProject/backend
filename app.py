from fastapi import FastAPI, HTTPException
from models import SignUp, UserAccount, EditPW
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
def create_user(user: SignUp):
    db = get_db_connection()
    hashed_password = hash_password(user.password)
    with db.cursor() as cursor:
        sql = "INSERT INTO USER (id, name, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (user.id, user.name, hashed_password))
        db.commit()
    db.close()
    return {"message": "User created successfully"}

@app.post("/sign-in")
def sign_in(user: UserAccount):
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "SELECT password FROM USER WHERE id = %s"
        cursor.execute(sql, (user.id))
        hashed_password = cursor.fetchone()['password']
        verified_password = verify_password(user.password, hashed_password)
        if verified_password:
            return {"message": "User login successfully"}
        else:
            raise HTTPException(status_code=403, detail="LoginError")

@app.delete("/withdraw")
def withdraw(user: UserAccount):
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "SELECT password FROM USER WHERE id = %s"
        cursor.execute(sql, (user.id))
        hashed_password = cursor.fetchone()['password']
        verified_password = verify_password(user.password, hashed_password)
        if verified_password:
            sql = "DELETE FROM USER WHERE id = %s"
            cursor.execute(sql, (user.id))
            db.commit()
            return {"message": "User Withdraw Success"}
        else:
            raise HTTPException(status_code=403, detail="WithDrawError")

@app.patch("/edit_pw")
def edit_pw(user: EditPW):
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "SELECT password FROM USER WHERE id = %s"
        cursor.execute(sql, (user.id))
        hashed_password = cursor.fetchone()['password']
        verified_password = verify_password(user.password, hashed_password)
        if verified_password:
            new_hashed_password = hash_password(user.new_password)
            sql = "UPDATE USER SET password = %s WHERE id = %s"
            cursor.execute(sql, (new_hashed_password, user.id))
            db.commit()
            return {"message": "User password updated successfully"}
        else:
            raise HTTPException(status_code=403, detail="PasswordError")