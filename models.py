from pydantic import BaseModel
from datetime import date
from fastapi import Form
from typing import Optional

class SignUp(BaseModel):
    id: str
    name: str
    password: str
    email: str

class SignIn(BaseModel):
    id: str
    password: str

class WithDraw(BaseModel):
    password: str  # 현재 비밀번호 확인용

class EditPW(BaseModel):
    password: str      # 현재 비밀번호
    new_password: str  # 새 비밀번호

class CreateTodo(BaseModel):
    status: str
    title: str
    contents: str
    todo_order: int  # todo_order를 선택적으로 변경

class EditTodo(BaseModel):
    todo_num : int
    status : str
    title : str
    contents : str
    todo_order: int