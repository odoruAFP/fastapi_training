from decouple import config
from fastapi import HTTPException
from typing import Union
import motor.motor_asyncio
from bson import ObjectId #https://www.mongodb.com/json-and-bson
from auth_utils import AuthJwtCsrf
import asyncio #Lecture15 Deploy to Render対応

MONGO_API_KEY = config('MONGO_API_KEY')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY)
client.get_io_loop = asyncio.get_event_loop #Lecture15 Deploy to Render対応
database = client.API_DB
collection_todo = database.todo
collection_user = database.user
auth  = AuthJwtCsrf()


def todo_serializer(todo) -> dict:
    return {
        "id": str(todo["_id"]),
        "title": todo["title"],
        "description": todo["description"]
    }

def user_serializer(user) -> dict:
    return{
        "id": str(user["_id"]),
        "email": user["email"]
    }

async def db_create_todo(data: dict) -> Union[dict, bool]:
    todo = await collection_todo.insert_one(data)
    new_todo = await collection_todo.find_one({"_id": todo.inserted_id})
    if new_todo:
        return todo_serializer(new_todo)
    return False

async def db_get_todos() -> list:
    todos = [] #MongoDBからのタスクの一覧を格納するための空の配列を作る
    #motorの機能を使ってタスクの一覧を取得する。findはmotorのメソッド
    #https://motor.readthedocs.io/en/stable/tutorial-asyncio.html
    #https://motor.readthedocs.io/en/stable/tutorial-asyncio.html#querying-for-more-than-one-document

    for todo in await collection_todo.find().to_list(length=100):
        todos.append(todo_serializer(todo))
    return todos

    #GETメソッドでIPを指定して特定のドキュメントをMongoDBから取得する処理
async def db_get_single_todo(id: str) -> Union[dict, bool]:
    todo = await collection_todo.find_one({"_id": ObjectID(id)})
    if todo:
        return todo_serializer(todo)
    return False

async def db_update_todo(id: str, data: dict) -> Union[dict, bool]:
    todo = await collection_todo.find_one({"_id": ObjectId(id)})
    if todo:
        updated_todo = await collection_todo.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
    #update_oneの返り値は、UpdateResultというクラスから作られたインスタンスとなっている
    #modified_countがゼロより大きければ更新に成功したという意味になる
        if (updated_todo.modified_count > 0):
            new_todo = await collection_todo.find_one({"_id": ObjectId(id)})
            return todo_serializer(new_todo)
    return False

async def db_delete_todo(id: str) -> bool:
    todo = await collection_todo.find_one({"_id": ObjectId(id)})
    if todo:
        deleted_todo = await collection_todo.delete_one({"_id": ObjectId(id)}) #delete_oneはmotorのメソッド
        if (deleted_todo.deleted_count > 0):
            return True
    return False

async def db_signup(data: dict) -> dict:
    email = data.get("email")
    password = data.get("password")
    overlap_user = await collection_user.find_one({"email": email}) #クライアントから届いたeメールアドレスがデータベース内のものと一致するか確認する処理
    if overlap_user:
        raise HTTPException(status_code=400, detail='Email is already taken')
    if not password or len(password) < 6:
        raise HTTPException(status_code=400, detail='Password too short')
    user = await collection_user.insert_one({"email": email, "password": auth.generate_hashed_pw(password)}) #ハッシュ化してデータベースに登録する
    #https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_motor_collection.html#motor.motor_asyncio.AsyncIOMotorCollection.insert_one
    new_user = await collection_user.find_one({"_id": user.inserted_id}) #MongoDBから取得した_idデータをnew_userに渡す処理
    return user_serializer(new_user)

async def db_login(data: dict) -> str:
    email =data.get("email")
    password = data.get("password")
    user = await collection_user.find_one({"email":email})
    if not user or not auth.verify_pw(password, user["password"]):
        raise HTTPException(
            status_code=401, detail='Invalid email or password'
        )
    token = auth.encode_jwt(user['email'])
    return token