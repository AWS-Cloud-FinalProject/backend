from fastapi import APIRouter, Depends, UploadFile, File, Form
from models import CreateDiary, EditDiary
from database import get_db_connection
from functions import verify_token, string_to_date
#from s3 import upload_to_s3

router = APIRouter()

@router.get("/get-diary-detail/{date}") 
def get_diary_detail(date: int, user: dict = Depends(verify_token)):
    user_id = user["sub"]
    date_obj = string_to_date(date)
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "SELECT * FROM DIARY WHERE id = %s AND diary_date = %s"
        cursor.execute(sql, (user_id, date_obj))
        result = cursor.fetchone()
    db.close()
    return result

# 일기 작성
@router.post("/add-diary/")
def add_diary(
    diary: CreateDiary,
    user: dict = Depends(verify_token)
):
    user_id = user["sub"]
    db = get_db_connection()
    #photo_url = None
    
    #if photo:
     #   photo_url = upload_to_s3(photo)
    with db.cursor() as cursor:
        sql = "INSERT INTO DIARY (id, title, contents, emotion, photo, diary_date) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (user_id, diary.title, diary.contents, diary.emotion, diary.photo, diary.diary_date))
        db.commit()
    db.close()
    return {"message": "Diary entry added successfully"}

# 일기 삭제
@router.delete("/delete-diary/{date}")
def delete_diary(date: int, user: dict = Depends(verify_token)):
    user_id = user["sub"]
    db = get_db_connection()
    date_obj = string_to_date(date)
    with db.cursor() as cursor:
        sql = "DELETE FROM DIARY WHERE id = %s AND date = %s"
        cursor.execute(sql, (user_id, date_obj))
        db.commit()
    db.close()
    return {"message": "Diary entry deleted successfully"}

# 일기 수정
@router.patch("/edit-diary/")
def edit_diary(diary: EditDiary, user: dict = Depends(verify_token)):
    user_id = user["sub"]
    db = get_db_connection()
    #photo_url = None
    
    #if photo:
     #   photo_url = upload_to_s3(photo)
    
    with db.cursor() as cursor:
        sql = "UPDATE DIARY SET title = %s, contents = %s, emotion = %s, photo = COALESCE(%s, photo) WHERE id = %s AND diary_date = %s"
        cursor.execute(sql, (diary.title, diary.contents, diary.emotion, diary.photo, user_id, diary.diary_date))
        db.commit()
    db.close()
    return {"message": "Diary entry updated successfully"}
