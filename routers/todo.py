from fastapi import APIRouter, Depends
from models import CreateTodo, EditTodo
from database import get_db_connection
from functions import verify_token

router = APIRouter()

#todolist
@router.get("/get-todo")
def get_todo(user: dict = Depends(verify_token)):
    user_id = user["sub"]
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "SELECT * FROM TODO WHERE id=%s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
    db.close()
    return result

# todo 생성 (여기도 토큰)
@router.post("/create-todo")
def create_todo(todo: CreateTodo):
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "INSERT INTO TODO (id, status, title, contents) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (todo.id, todo.status, todo.title, todo.contents))
        db.commit()
    db.close()
    return {"message": "Todo Create Successfully"}

# todo 삭제 (여기도 토큰)
@router.delete("/delete-todo/{todo_num}")
def delete_todo(todo_num: int):
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "DELETE FROM TODO WHERE todo_num = %s"
        cursor.execute(sql, (todo_num))
        db.commit()
        return {"message": "Todo Delete Success"}
    
# todo 수정 (여기도 토큰)
@router.patch("/edit-todo")
def edit_pw(todo: EditTodo):
    db = get_db_connection()
    with db.cursor() as cursor:
        sql = "UPDATE TODO SET status = %s, title = %s, contents = %s WHERE todo_num = %s"
        cursor.execute(sql, (todo.status, todo.title, todo.contents, todo.todo_num))
        db.commit()
        return {"message": "User password updated successfully"}