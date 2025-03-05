from fastapi import APIRouter, Depends, UploadFile, File, Form
from models import CreateDiary, EditDiary
from database import get_db_connection
from functions import verify_token
from s3 import upload_to_s3

router = APIRouter()

@router.get("/get-diary-detail/{year}/{month}/{day}")
def get_diary_detail(year: int, month: int, day: int, user: dict = Depends(verify_token)):
    user_id = user["sub"]
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "SELECT * FROM DIARY WHERE id = %s"
        cursor.execute(sql, (user_id, f"{year}-{month:02d}-{day:02d}"))
        result = cursor.fetchone()
    db.close()
    return result

# 일기 작성
@router.post("/add-diary/")
def add_diary(
    title: str = Form(...),
    contents: str = Form(...),
    emotion: str = Form(...),
    photo: UploadFile = File(None),
    user: dict = Depends(verify_token)
):
    user_id = user["sub"]
    db = get_db_connection()
    photo_url = None
    
    if photo:
        photo_url = upload_to_s3(photo)
    
    with db.cursor() as cursor:
        sql = "INSERT INTO DIARY (id, title, contents, emotion, photo, date) VALUES (%s, %s, %s, %s, %s, CURDATE())"
        cursor.execute(sql, (user_id, title, contents, emotion, photo_url))
        db.commit()
    db.close()
    return {"message": "Diary entry added successfully"}

# 일기 삭제
@router.delete("/delete-diary/{year}/{month}/{day}")
def delete_diary(year: int, month: int, day: int, user: dict = Depends(verify_token)):
    user_id = user["sub"]
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "DELETE FROM DIARY WHERE id = %s AND date = %s"
        cursor.execute(sql, (user_id, f"{year}-{month:02d}-{day:02d}"))
        db.commit()
    db.close()
    return {"message": "Diary entry deleted successfully"}

# 일기 수정
@router.patch("/edit-diary/")
def edit_diary(
    date: str = Form(...),
    title: str = Form(...),
    contents: str = Form(...),
    emotion: str = Form(...),
    photo: UploadFile = File(None),
    user: dict = Depends(verify_token)
):
    user_id = user["sub"]
    db = get_db_connection()
    photo_url = None
    
    if photo:
        photo_url = upload_to_s3(photo)
    
    with db.cursor() as cursor:
        sql = "UPDATE DIARY SET title = %s, contents = %s, emotion = %s, photo = COALESCE(%s, photo) WHERE id = %s AND date = %s"
        cursor.execute(sql, (title, contents, emotion, photo_url, user_id, date))
        db.commit()
    db.close()
    return {"message": "Diary entry updated successfully"}
