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
    todo_order : int

class EditTodo(BaseModel):
    todo_num : int
    status : str
    title : str
    contents : str
<<<<<<< HEAD

class Diary(BaseModel):
    date: date
    id: str
    title: str
    contents: str
    photo: str
    emotion: str
=======
    todo_order : int
>>>>>>> 971cf4c0f5d5161873f3d6b4f8a6aec35995edd8
