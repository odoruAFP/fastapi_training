from pydantic import BaseModel
from typing import Optional
from decouple import config

CSRF_KEY = config('CSRF_KEY')


class CsrfSettings(BaseModel):
    secret_key: str = CSRF_KEY


class Todo(BaseModel):
    id: str
    title:str
    description:str


class TodoBody(BaseModel):
    title: str
    description: str


class SuccessMsg(BaseModel):
    message: str


class UserBody(BaseModel): #ユーザー関係の型を定義しておく クライアントから送られて来るemailとpasswordの型になる stringで定義しておく
    email: str
    password: str


class UserInfo(BaseModel): #レスポンスを定義する 複数のエンドポイントで使いまわすことを想定する
    id: Optional[str] = None  #idを任意の値に設定する
    email: str

class Csrf(BaseModel):
    csrf_token: str
