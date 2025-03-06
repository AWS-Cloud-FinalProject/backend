from fastapi import APIRouter, Depends
from models import CreateTodo, EditTodo
from database import get_db_connection
from functions import verify_token
from collections import defaultdict

router = APIRouter()

# todo list
@router.get("/get-todo")
def get_todo(user: dict = Depends(verify_token)):
    user_id = user["sub"]
    db = get_db_connection()
    with db.cursor() as cursor:
        # todo_order 기준으로 오름차순 정렬 추가
        sql = "SELECT * FROM TODO WHERE id = %s ORDER BY todo_order ASC"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
    db.close()

    grouped_todos = defaultdict(list)
    for row in result:
        status = row["status"]
        todo_item = {
            "todo_num": row["todo_num"],
            "id": row["id"],
            "title": row["title"],
            "contents": row["contents"],
            "todo_order": row["todo_order"]
        }
        grouped_todos[status].append(todo_item)

    return grouped_todos

# todo 생성
@router.post("/create-todo")
def create_todo(todo: CreateTodo, user: dict = Depends(verify_token)):
    user_id = user["sub"]
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "INSERT INTO TODO (id, status, title, contents, todo_order) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (user_id, todo.status, todo.title, todo.contents, todo.todo_order))
        db.commit()
    db.close()
    return {"message": "Todo Create Successfully"}

# todo 삭제
@router.delete("/delete-todo/{todo_num}")
def delete_todo(todo_num: int, user: dict = Depends(verify_token)):
    user_id = user["sub"]
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "DELETE FROM TODO WHERE id = %s AND todo_num = %s"
        cursor.execute(sql, (user_id, todo_num))
        db.commit()
        return {"message": "Todo Delete Success"}
    
# todo 수정
@router.patch("/edit-todo")
def edit_todo(todo: EditTodo, _: dict = Depends(verify_token)):
    db = get_db_connection()
    with db.cursor() as cursor:
        # 기존 todo_order를 업데이트하기 전에, 변경된 위치에 영향을 받는 todo들 순서 업데이트
        if todo.todo_order != todo.todo_num:  # `todo_order`가 변경될 경우
            # 해당 컬럼 내 todo_order를 한 칸씩 밀어내는 처리
            sql_update_order = """
                UPDATE TODO
                SET todo_order = CASE 
                    WHEN todo_order >= %s THEN todo_order + 1
                    ELSE todo_order
                END
                WHERE status = %s AND todo_order >= %s AND todo_num != %s
            """
            cursor.execute(sql_update_order, (todo.todo_order, todo.status, todo.todo_order, todo.todo_num))

        # 이후 본래 todo의 정보를 수정
        sql = "UPDATE TODO SET status = %s, title = %s, contents = %s, todo_order = %s WHERE todo_num = %s"
        cursor.execute(sql, (todo.status, todo.title, todo.contents, todo.todo_order, todo.todo_num))
        db.commit()
        return {"message": "Todo updated successfully"}