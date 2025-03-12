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
        sql = "SELECT * FROM TODO WHERE id = %s"
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
            "contents": row["contents"]
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
            sql = "INSERT INTO TODO (id, status, title, contents) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (user_id, todo.status, todo.title, todo.contents))
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
            # todo 정보 수정
            sql = "UPDATE TODO SET status = %s, title = %s, contents = %s WHERE todo_num = %s AND id = %s"
            cursor.execute(sql, (todo.status, todo.title, todo.contents, todo.todo_num, user_id))
            db.commit()
        db.close()
        return {"message": "Todo updated successfully"}
    except Exception as e:
        print(f"Error updating todo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating todo: {str(e)}")
