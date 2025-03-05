from fastapi import APIRouter, Depends
from models import CreateTodo, EditTodo
from database import get_db_connection
from functions import verify_token

router = APIRouter()

# todo list
@router.get("/get-todo")
def get_todo(user: dict = Depends(verify_token)):
    user_id = user["sub"]
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "SELECT * FROM TODO WHERE id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
    db.close()
    return result

# todo 생성
@router.post("/create-todo")
def create_todo(todo: CreateTodo, user: dict = Depends(verify_token)):
    user_id = user["sub"]
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "INSERT INTO TODO (id, status, title, contents) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (user_id, todo.status, todo.title, todo.contents))
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
        sql = "UPDATE TODO SET status = %s, title = %s, contents = %s WHERE todo_num = %s"
        cursor.execute(sql, (todo.status, todo.title, todo.contents, todo.todo_num))
        db.commit()
        return {"message": "Todo updated successfully"}