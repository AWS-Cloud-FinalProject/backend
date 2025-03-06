from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from database import get_db_connection
from functions import verify_token, string_to_date
from routers.s3 import upload_to_s3, delete_file_from_s3
from datetime import date
from pathlib import Path

router = APIRouter()

@router.get("/get-diary-detail/{date}") 
def get_diary_detail(
    date: int,
    user: dict = Depends(verify_token)):
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
    diary_date: date = Form(...),
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
        #user_folder = f"{user_id}/"
        photo_url = upload_to_s3(photo, "webdiary", str(user_id), str(diary_date))
    with db.cursor() as cursor:
        sql = "INSERT INTO DIARY (id, title, contents, emotion, photo, diary_date) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (user_id, title, contents, emotion, photo_url, diary_date))
        db.commit()
    db.close()
    return {"message": "Diary entry added successfully"}

# 일기 삭제
@router.delete("/delete-diary/{date}")
def delete_diary(date: int, user: dict = Depends(verify_token)):
    user_id = user["sub"]
    db = get_db_connection()
    date_obj = string_to_date(date)
     # "YYYY-MM-DD" 형식에서 파일 이름을 생성 (파일 확장자는 .jpg로 고정)
    date_str = date_obj.replace('-', '')
    file_name = f"{date_str}{Path(photo.filename).suffix}"  # 예: 20250306.jpg

    # DB에서 일기 삭제
    try:
        with db.cursor() as cursor:
            sql = "DELETE FROM DIARY WHERE id = %s AND diary_date = %s"
            cursor.execute(sql, (user_id, date_str))
            db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB에서 일기 삭제 중 오류 발생: {str(e)}")

        # S3에서 파일 삭제
    try:
        delete_file_from_s3(user_id, file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 파일 삭제 중 오류 발생: {str(e)}")

    db.close()
    return {"message": "Diary entry deleted successfully"}

# 일기 수정
@router.patch("/edit-diary/")
def edit_diary(
    diary_date: date  = Form(...),
    title: str = Form(...),
    contents: str = Form(...),
    emotion: str = Form(...), 
    photo: UploadFile = File(None), #사진은 별도로 업로드
    user: dict = Depends(verify_token)):
    user_id = user["sub"]
    db = get_db_connection()
    photo_url = None
    
    if photo:
       #user_folder = f"{user_id}"
       photo_url = upload_to_s3(photo, "webdiary", user_id, str(diary_date))
    
    with db.cursor() as cursor:
        sql = "UPDATE DIARY SET title = %s, contents = %s, emotion = %s, photo = COALESCE(%s, photo) WHERE id = %s AND diary_date = %s"
        cursor.execute(sql, (title, contents, emotion, photo, user_id, diary_date))
        db.commit()
    db.close()
    return {"message": "Diary entry updated successfully"}
