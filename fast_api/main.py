from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import route_todo, route_auth
from schemas import SuccessMsg, CsrfSettings #importしているのは「型」である
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

  #https://nununu.hatenablog.jp/entry/2021/05/21/095841
  #Windows開発機では functions-framework-pythonのローカルエミュレータを動かせない

  #Udemy講座 FastAPIのSection6で動画に従ってfastapiモジュールをインストールして
  #動作を確認することまで出来たのだが、GUNICORNだけはWindows版Python 3.9に対応した
  #モジュールが配布されておらず行き詰ってしまった。そうとわかっていたら最初からこの
  #講座は受講しなかった。→2022年5月23日にcondaでインストールした記録が残されていた。

  #FastAPIとは？PythonのWebフレームワークでWebAPIを開発しよう！（↓詳しく書かれている）
  #https://aiacademy.jp/media/?p=988

app = FastAPI()
app.include_router(route_todo.router)
app.include_router(route_auth.router)
origins = ['http://localhost:3000'] #後でReactから呼ぶためのホワイトリスト
app.add_middleware(
    CORSMiddleware,
    #allow_origins=origins,
    allow_origins=["*"],  # 全てのオリジンからのアクセスを許可 (必要に応じて適切なオリジンを指定) by ChatGPT
    allow_credentials=True,
    #allow_methods=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # 適切なHTTPメソッドを許可 by ChatGPT
    allow_headers=["*"],
)

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()


@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/", response_model = SuccessMsg)
def root():
    return {"message": "Welcome to Fast API"}
