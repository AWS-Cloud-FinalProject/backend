from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from database import get_db_connection
from functions import verify_token, string_to_date
from routers.s3 import upload_to_s3, delete_file_from_s3
from datetime import date
from urllib.parse import urlparse
import os

router = APIRouter()

@router.get("/get-diary/{year_month}")
def get_diary(year_month: str, user: dict = Depends(verify_token)):
    user_id = user["sub"]
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            # 연도와 월에 해당하는 일기 데이터 조회
            sql = """
                SELECT DATE_FORMAT(diary_date, '%%Y-%%m-%%d') AS date, title, emotion 
                FROM DIARY 
                WHERE id = %s AND DATE_FORMAT(diary_date, '%%Y%%m') = %s
                ORDER BY diary_date
            """
            cursor.execute(sql, (user_id, year_month))
            result = cursor.fetchall()

            # 결과를 JSON 형식으로 변환
            diary_entries = [{"date": row["date"], "title": row["title"], "emotion": row["emotion"]} for row in result]

            return diary_entries

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    finally:
        db.close()

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

    try:
        with db.cursor() as cursor:
            # 해당 날짜의 사진 URL 조회
            sql = "SELECT photo FROM DIARY WHERE id = %s AND diary_date = %s"
            cursor.execute(sql, (user_id, date_obj))
            result = cursor.fetchone()
        
        if not result or not result["photo"]:
            raise HTTPException(status_code=404, detail="사진이 존재하지 않음")

        photo_url = result["photo"]

        # URL에서 파일 확장자 추출
        parsed_url = urlparse(photo_url)
        file_extension = os.path.splitext(parsed_url.path)[-1]  # 예: ".jpg" 또는 ".png"

        if not file_extension:
            raise HTTPException(status_code=500, detail="파일 확장자를 찾을 수 없음")

        # 파일 이름 생성
        file_name = f"{date_obj.replace('-', '')}{file_extension}"

        # S3에서 파일 삭제
        delete_file_from_s3(user_id, file_name)

        # DB에서 일기 삭제
        with db.cursor() as cursor:
            sql = "DELETE FROM DIARY WHERE id = %s AND diary_date = %s"
            cursor.execute(sql, (user_id, date_obj))
            db.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")

    finally:
        db.close()

    return {"message": "Diary entry and photo deleted successfully"}

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
       photo_url = upload_to_s3(photo, "webdiary", user_id, str(diary_date))
    
    with db.cursor() as cursor:
        sql = "UPDATE DIARY SET title = %s, contents = %s, emotion = %s, photo = COALESCE(%s, photo) WHERE id = %s AND diary_date = %s"
        cursor.execute(sql, (title, contents, emotion, photo, user_id, diary_date))
        db.commit()
    db.close()
    return {"message": "Diary entry updated successfully"}