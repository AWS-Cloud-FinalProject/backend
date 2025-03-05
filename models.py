from pydantic import BaseModel
from datetime import date
from fastapi import Form

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
    diary_date: date = Form(...)
    title: str = Form(...)
    contents: str = Form(...)
    photo: str = None
    emotion: str = Form(...)

class EditDiary(BaseModel):
    diary_date: date  = Form(...)
    title: str = Form(...)
    contents: str = Form(...)
    emotion: str = Form(...)
    photo: str = None