from fastapi import APIRouter, Depends, UploadFile, File, Form
from database import get_db_connection
from functions import verify_token
from routers.s3 import upload_to_s3, delete_file_from_s3
from typing import Optional

router = APIRouter()

# 글 목록 가져오기
@router.get("/get-posts")
def get_posts(user: dict = Depends(verify_token)):
    db = get_db_connection()
    user_id = user["username"]
    try:
        with db.cursor() as cursor:
            sql = "SELECT * FROM COMMUNITY ORDER BY created_at DESC"
            cursor.execute(sql)
            result = cursor.fetchall()

            # 내 글 여부를 판단하여 mine 필드 추가
            for post in result:
                post["mine"] = True if post["id"] == user_id else False

        return result
    finally:
        db.close()

# 내 글 목록 가져오기
@router.get("/get-my-posts")
def get_my_posts(user: dict = Depends(verify_token)):
    db = get_db_connection()
    user_id = user["username"]
    try:
        with db.cursor() as cursor:
            sql = "SELECT * FROM COMMUNITY WHERE id = %s ORDER BY created_at DESC"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
        return result
    finally:
        db.close()

# 글 작성
@router.post("/create-post")
def create_post(
    contents: str = Form(...),
    photo: UploadFile = File(None),
    user: dict = Depends(verify_token)
):
    db = get_db_connection()
    user_id = user["username"]
    photo_url = None

    # 게시글을 먼저 DB에 추가
    try:
        with db.cursor() as cursor:
            # INSERT 쿼리 실행
            sql = "INSERT INTO COMMUNITY (id, contents) VALUES (%s, %s)"
            cursor.execute(sql, (user_id, contents))
            # 방금 삽입된 post_id 가져오기
            post_id = cursor.lastrowid  # AUTO_INCREMENT로 생성된 ID

            # 사진이 있다면 업로드 처리
            if photo:
                photo_url = upload_to_s3("post", photo, "webdiary", "COMMUNITY", post_id)

            # 사진 URL 업데이트
            if photo_url:
                sql_update = "UPDATE COMMUNITY SET photo = %s WHERE post_num = %s"
                cursor.execute(sql_update, (photo_url, post_id))

        db.commit()
    finally:
        db.close()

    return {"message": "Post created successfully"}

# 글 수정
@router.patch("/edit-post/{post_id}")
def update_post(
    post_id: int, 
    contents: str = Form(...),
    photo: Optional[UploadFile] = File(None),  # 빈 값 가능
    photo_provided: Optional[bool] = Form(False),  # 프론트엔드에서 사진 변경 여부 전달
    user: dict = Depends(verify_token)
):
    db = get_db_connection()
    user_id = user["username"]
    try:
        with db.cursor() as cursor:
            # 기존 사진 URL 가져오기
            sql_select = "SELECT photo FROM COMMUNITY WHERE post_num = %s AND id = %s"
            cursor.execute(sql_select, (post_id, user_id))
            result = cursor.fetchone()
            old_photo_url = result["photo"] if result else None

            photo_url = old_photo_url  # 기본적으로 기존 사진 유지

            # 사용자가 명시적으로 사진을 삭제하려는 경우
            if photo_provided and photo is None:
                if old_photo_url:
                    delete_file_from_s3(user_id, old_photo_url)  # S3에서 삭제
                photo_url = None  # DB에서도 삭제

            # 새로운 사진이 업로드된 경우 → 기존 사진 삭제 후 업로드
            elif photo_provided and photo:
                if old_photo_url:
                    delete_file_from_s3(user_id, old_photo_url)  # 기존 파일 삭제
                photo_url = upload_to_s3("post", photo, "webdiary", "COMMUNITY", post_id)  # 새 파일 업로드

            # 게시글 내용 업데이트
            sql_update = """
            UPDATE COMMUNITY 
            SET contents = %s, photo = %s 
            WHERE post_num = %s AND id = %s
            """
            cursor.execute(sql_update, (contents, photo_url, post_id, user_id))
        db.commit()
    finally:
        db.close()
    return {"message": "Post updated successfully"}

# 글 삭제
@router.delete("/delete-post/{post_id}")
def delete_post(post_id: int, user: dict = Depends(verify_token)):
    db = get_db_connection()
    user_id = user["username"]
    try:
        with db.cursor() as cursor:
            # 게시글 사진 URL 가져오기
            sql_select = "SELECT photo FROM COMMUNITY WHERE post_num = %s AND id = %s"
            cursor.execute(sql_select, (post_id, user_id))
            result = cursor.fetchone()
            old_photo_url = result["photo"] if result else None

            # 사진이 있으면 S3에서 삭제
            if old_photo_url:
                delete_file_from_s3(user_id, old_photo_url)

            # 게시글 삭제
            sql_delete = "DELETE FROM COMMUNITY WHERE post_num = %s AND id = %s"
            cursor.execute(sql_delete, (post_id, user_id))
        db.commit()
    finally:
        db.close()
    return {"message": "Post deleted successfully"}
