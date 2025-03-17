from fastapi import APIRouter, Depends, HTTPException
from database import get_db_connection
from typing import List
from functions import verify_token


router = APIRouter()

# 유저 팔로우
@router.post("/follow/{following_id}")
def follow_user(following_id: str, user: dict = Depends(verify_token)):
    db = get_db_connection()
    user_id = user["username"]
    try:
        if (following_id == user_id):
            raise HTTPException(status_code=400, detail="You cannot follow yourself")
        with db.cursor() as cursor:
            sql = """
                INSERT INTO COMMUNITY_FOLLOW (follower_id, following_id)
                VALUES (%s, %s)
            """
            cursor.execute(sql, (user_id, following_id))
        db.commit()
    finally:
        db.close()
    return {"message": "Followed successfully"}

# 유저 언팔로우
@router.delete("/unfollow/{following_id}")
def unfollow_user(following_id: str, user: dict = Depends(verify_token)):
    db = get_db_connection()
    user_id = user["username"]
    try:
        with db.cursor() as cursor:
            sql = "DELETE FROM COMMUNITY_FOLLOW WHERE follower_id = %s AND following_id = %s"
            cursor.execute(sql, (user_id, following_id))
        db.commit()
    finally:
        db.close()
    return {"message": "Unfollowed successfully"}

# 팔로잉 목록 가져오기
@router.get("/following/{following_id}")
def get_following_list(following_id: str, _: dict = Depends(verify_token)):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            sql = "SELECT following_id FROM COMMUNITY_FOLLOW WHERE follower_id = %s"
            cursor.execute(sql, (following_id,))
            result = cursor.fetchall()
        return [row["following_id"] for row in result]
    finally:
        db.close()

# 팔로워 목록 가져오기
@router.get("/follower/{follower_id}")
def get_follower_list(follower_id: str, _: dict = Depends(verify_token)):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            sql = "SELECT follower_id FROM COMMUNITY_FOLLOW WHERE following_id = %s"
            cursor.execute(sql, (follower_id,))
            result = cursor.fetchall()
        return [row["follower_id"] for row in result]
    finally:
        db.close()