from pydantic import BaseModel
from datetime import date

class User(BaseModel):
    id: str
    name: str
    password: str

class Todo(BaseModel):
    todo_num: int
    id: str
    status: str
    title: str
    contents: str

class Diary(BaseModel):
    date: date
    id: str
    title: str
    contents: str
    photo: str
    emotion: str
