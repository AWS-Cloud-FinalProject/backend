from pydantic import BaseModel
from datetime import date

class SignUp(BaseModel):
    id: str
    name: str
    password: str

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

class EditTodo(BaseModel):
    todo_num : int
    status : str
    title : str
    contents : str

class CreateDiary(BaseModel):
    date: date
    id: str
    title: str
    contents: str
    photo: str
    emotion: str

class EditDiary(BaseModel):
    title: str
    contents: str
    emotion: str
    photo: str = None