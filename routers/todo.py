from fastapi import APIRouter, Depends
from models import CreateTodo, EditTodo
from database import get_db_connection
from functions import verify_token
from collections import defaultdict
from fastapi import HTTPException

router = APIRouter()

# todo list
@router.get("/get-todo")
def get_todo(user: dict = Depends(verify_token)):
    user_id = user["username"]
    db = get_db_connection()
    with db.cursor() as cursor:
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
    try:
        user_id = user["username"]
        db = get_db_connection()
        with db.cursor() as cursor:
            sql = "INSERT INTO TODO (id, status, title, contents, todo_order) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (user_id, todo.status, todo.title, todo.contents, todo.todo_order))
            db.commit()
        db.close()
        return {"message": "Todo Create Successfully"}
    except Exception as e:
        print(f"Error creating todo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating todo: {str(e)}")

# todo 삭제
@router.delete("/delete-todo/{todo_num}")
def delete_todo(todo_num: int, user: dict = Depends(verify_token)):
    user_id = user["username"]
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "DELETE FROM TODO WHERE id = %s AND todo_num = %s"
        cursor.execute(sql, (user_id, todo_num))
        db.commit()
        return {"message": "Todo Delete Success"}
    
# todo 수정
@router.patch("/edit-todo")
def edit_todo(todo: EditTodo, user: dict = Depends(verify_token)):
    try:
        user_id = user["username"]
        db = get_db_connection()
        with db.cursor() as cursor:
            # 기존 todo_order를 업데이트하기 전에, 변경된 위치에 영향을 받는 todo들 순서 업데이트
            # 1. todo_order를 0부터 1씩 증가하도록 재배열
            sql_reorder = """
                UPDATE TODO t
                JOIN (
                    SELECT todo_num, 
                           ROW_NUMBER() OVER (ORDER BY todo_order) - 1 AS new_rank
                    FROM TODO
                    WHERE status = %s
                ) AS new_order
                ON t.todo_num = new_order.todo_num
                SET t.todo_order = new_order.new_rank
            """
            cursor.execute(sql_reorder, (todo.status,))

            # 2. todo_order가 변경될 경우 기존 값들을 한 칸씩 밀어내는 처리
            if todo.todo_order != todo.todo_num:
                sql_update_order = """
                    UPDATE TODO
                    SET todo_order = CASE 
                        WHEN todo_order >= %s THEN todo_order + 1
                        ELSE todo_order
                    END
                    WHERE status = %s AND todo_order >= %s AND todo_num != %s
                """
                cursor.execute(sql_update_order, (todo.todo_order, todo.status, todo.todo_order, todo.todo_num))

            # 3. 이후 본래 todo의 정보를 수정
            sql = "UPDATE TODO SET status = %s, title = %s, contents = %s, todo_order = %s WHERE todo_num = %s AND id = %s"
            cursor.execute(sql, (todo.status, todo.title, todo.contents, todo.todo_order, todo.todo_num, user_id))
            db.commit()
        db.close()
        return {"message": "Todo updated successfully"}
    except Exception as e:
        print(f"Error updating todo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating todo: {str(e)}")
