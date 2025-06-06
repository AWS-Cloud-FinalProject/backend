from pydantic import BaseModel

class SignUp(BaseModel):
    id: str
    name: str
    password: str
    email: str

class SignIn(BaseModel):
    id: str
    password: str

class WithDraw(BaseModel):
    password: str

class EditPW(BaseModel):
    password: str
    new_password: str

class CreateTodo(BaseModel):
    status: str
    title: str
    contents: str
    todo_order: int

class EditTodo(BaseModel):
    todo_num: int
    status: str
    title: str
    contents: str
    todo_order: int
