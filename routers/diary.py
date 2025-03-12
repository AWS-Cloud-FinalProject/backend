from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from database import get_db_connection
from functions import verify_token, string_to_date
from routers.s3 import upload_to_s3, delete_file_from_s3, update_s3_file
from datetime import date
from urllib.parse import urlparse
from typing import Optional
import pymysql.cursors
import os

router = APIRouter()

@router.get("/get-diary/{year_month}")
def get_diary(year_month: str, user: dict = Depends(verify_token)):
    user_id = user["username"]
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            # 현재 연도와 월을 추출
            year = int(year_month[:4])
            month = int(year_month[4:])

            # 이전 달 계산
            prev_year = year if month > 1 else year - 1
            prev_month = month - 1 if month > 1 else 12
            prev_year_month = f"{prev_year}{prev_month:02d}"

            # 다음 달 계산
            next_year = year if month < 12 else year + 1
            next_month = month + 1 if month < 12 else 1
            next_year_month = f"{next_year}{next_month:02d}"

            # 연속된 3개월(이전 달, 현재 달, 다음 달) 데이터를 가져옴
            sql = """
                SELECT DATE_FORMAT(diary_date, '%%Y-%%m-%%d') AS date, emotion 
                FROM DIARY 
                WHERE id = %s 
                AND DATE_FORMAT(diary_date, '%%Y%%m') IN (%s, %s, %s)
                ORDER BY diary_date
            """
            cursor.execute(sql, (user_id, prev_year_month, year_month, next_year_month))
            result = cursor.fetchall()

            # 결과를 JSON 형식으로 변환
            diary_entries = [{"date": row["date"], "emotion": row["emotion"]} for row in result]

            return diary_entries

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    finally:
        db.close()

@router.get("/get-diary-detail/{date}") 
def get_diary_detail(
    date: int,
    user: dict = Depends(verify_token)):
    user_id = user["username"]
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
    photo: Optional[UploadFile] = File(None),  # Optional 추가
    user: dict = Depends(verify_token)
):
    user_id = user["username"]  # Cognito는 'sub' 대신 'username' 사용
    db = get_db_connection()
    photo_url = None

    if photo and photo.filename:  # 파일이 실제로 존재하는지 확인
        photo_url = upload_to_s3(photo, "webdiary", str(user_id), str(diary_date))
    with db.cursor() as cursor:
        sql = "INSERT INTO DIARY (id, title, contents, emotion, photo, diary_date) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (user_id, title, contents, emotion, photo_url, diary_date))
        db.commit()
    db.close()
    return {"message": "Diary entry added successfully"}

#일기 삭제
@router.delete("/delete-diary/{date}")
def delete_diary(date: int, user: dict = Depends(verify_token)):
    user_id = user["username"]
    db = get_db_connection()
    date_obj = string_to_date(date)

    try:
        with db.cursor() as cursor:
            # 사진 URL 조회
            sql = "SELECT photo FROM DIARY WHERE id = %s AND diary_date = %s"
            cursor.execute(sql, (user_id, date_obj))
            result = cursor.fetchone()

        # 사진이 존재하면 S3에서 삭제
        if result and result["photo"]:
            photo_url = result["photo"]
            parsed_url = urlparse(photo_url)
            object_key = parsed_url.path.lstrip("/")  # '/bucket/path/to/file.jpg' -> 'path/to/file.jpg'
            delete_file_from_s3(user_id, object_key)

        # 사진 유무와 관계없이 DB에서 일기 삭제
        with db.cursor() as cursor:
            sql = "DELETE FROM DIARY WHERE id = %s AND diary_date = %s"
            cursor.execute(sql, (user_id, date_obj))
            db.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")

    finally:
        db.close()

    return {"message": "Diary entry deleted successfully"}

# 일기 수정
@router.patch("/edit-diary/")
def edit_diary(
    diary_date: date = Form(...),
    title: str = Form(...),
    contents: str = Form(...),
    emotion: str = Form(...),
    photo: Optional[UploadFile] = File(None),
    user: dict = Depends(verify_token)
):
    user_id = user["username"]
    db = get_db_connection()

    with db.cursor() as cursor:
        # 기존 사진 URL 가져오기
        sql_select = "SELECT photo FROM DIARY WHERE id = %s AND diary_date = %s"
        cursor.execute(sql_select, (user_id, diary_date))
        result = cursor.fetchone()
        old_photo_url = result["photo"] if result else None

        photo_url = old_photo_url  # 기본적으로 기존 사진 유지

        # 사용자가 `photo` 필드를 빈 값으로 보낸 경우 → 기존 사진 삭제
        if photo is None:
            if old_photo_url:
                delete_file_from_s3(user_id, old_photo_url)  # S3에서 삭제
            photo_url = None  # DB에서도 삭제

        # 새로운 사진이 업로드된 경우 → 기존 사진 삭제 후 업로드
        elif photo:
            if old_photo_url:
                delete_file_from_s3(user_id, old_photo_url)  # 기존 파일 삭제
            photo_url = upload_to_s3(photo, "webdiary", str(user_id), str(diary_date))  # 새 파일 업로드

        # DB 업데이트
        sql_update = """
        UPDATE DIARY 
        SET title = %s, contents = %s, emotion = %s, photo = %s 
        WHERE id = %s AND diary_date = %s
        """
        cursor.execute(sql_update, (title, contents, emotion, photo_url, user_id, diary_date))
        db.commit()

    db.close()
    return {"message": "Diary entry updated successfully"}