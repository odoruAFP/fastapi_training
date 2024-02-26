from fastapi import APIRouter
from fastapi import Response, Request, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from schemas import Todo, TodoBody, SuccessMsg
from database import db_create_todo, db_get_todos, db_get_single_todo, db_update_todo, db_delete_todo
from starlette.status import HTTP_201_CREATED
from typing import List
from fastapi_csrf_protect import CsrfProtect
from auth_utils import AuthJwtCsrf

router = APIRouter()
auth = AuthJwtCsrf() #Lecture 14 CSRF Token 9:18 入力するのを忘れていた
#https://teratail.com/questions/289300?link=qa_related_sp
#[Python] FastAPI POSTのとき, 405 Method Not Allowed
#https://qiita.com/uturned0/items/9c3d19c1f846a07ec779
#はじめての FastAPI（前編）
#ブラウザからPOSTメソッドを送信できるChrome拡張「Advanced REST client」
#https://www.koikikukan.com/archives/2015/12/15-000300.php
#そもそもブラウザからは簡単にPOSTメソッドは送信できないことがわかった。
#フォームデータの送信
#https://developer.mozilla.org/ja/docs/Learn/Forms/Sending_and_retrieving_form_dat

@router.post("/api/todo", response_model = Todo)
async def create_todo(request: Request, response: Response, data: TodoBody, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await db_create_todo(todo)
    response.status_code = HTTP_201_CREATED
    response.set_cookie(key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return res
    raise HTTPException(
        status_code=404, detail = "Create task failed by Koji"
    )

#タスクの一覧を取得するためのエンドポイント
@router.get("/api/todo", response_model=List[Todo])
async def get_todos(request: Request):
    #auth.verify_jwt(request) 単独では引っかかる Herokuの代わりにRenderへデプロイするときも要らない Lecture 15 Deploy to Render
    res = await db_get_todos()
    return res

#特定のIDについてひとつのタスクを取得するためのGETメソッド
@router.get("/api/todo/{id}", response_model=Todo)
async def get_single_todo(request: Request, response: Response, id: str):
    new_token, _ = auth.verify_update_jwt(request) #受け取らないpayloadはアンダーバー'_'で記述する
    res = await db_get_single_todo(id)
    response.set_cookie(key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return res
    raise HTTPException( status_code=404, detail=f"Task of ID:{id} doesn't exist") #「f」はフォーマット文

@router.put("/api/todo/{id}", response_model=Todo) #更新用のエンドポイント
async def update_todo(request: Request, response: Response, id: str, data: TodoBody, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await db_update_todo(id, todo)
    response.set_cookie(key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return res
    raise HTTPException(
        status_code=404, detail="Update task failed"
    )

@router.delete("/api/todo/{id}", response_model=SuccessMsg)
async def delete_todo(request: Request, response: Response, id: str, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(request, csrf_protect, request.headers)
    res = await db_delete_todo(id)
    response.set_cookie(key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return {'message': 'Successfully deleted'}
    raise HTTPException(
        status_code=404, detail="Delete task failed"
    )