import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta
from decouple import config

JWT_KEY = config('JWT_KEY')


class AuthJwtCsrf():
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto") #インスタンス作成
    secret_key = JWT_KEY

    def generate_hashed_pw(self , password) -> str:
        return self.pwd_ctx.hash(password) #ユーザーが入力したパスワードをハッシュ化して返す処理

    def verify_pw(self, plain_pw, hashed_pw) -> bool:
        return self.pwd_ctx.verify(plain_pw, hashed_pw) #ユーザーが入力した平文のパスワードとデータベースに保存されているハッシュ化されたパスワードを比較してブーリアンで返す

    def encode_jwt(self, email) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=5),    #JWTの有効期限を5分間に設定
            'iat': datetime.utcnow(),                                   #JWTが生成された日時
            'sub': email                                                #ユーザーを一意に識別する情報
        }
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm='HS256'
        )

    def decode_jwt(self, token) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithm['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401, detail='The JWT has expired')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail='JWT is not valid') #空のトークンや、JWTと異なる様式が来たときの処理
    
    def verify_jwt(self, request) -> str:
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(
                status_code=401, detail='No JWT exist: may not set yet or deleted'
            )
        _, _, value = token.partition(" ") #いちばん後ろの値だけを取り込む
        subject = self.decode_jwt(value)
        return subject

    def verify_update_jwt(self, request) -> tuple[str, str]:
        subject = self.verify_jwt(request)
        new_token = self.encode_jwt(subject)
        return new_token, subject
    
    def verify_csrf_update_jwt(self, request, csrf_protect, headers) -> str:
        csrf_token = csrf_protect.get_csrf_from_headers(headers)
        csrf_protect.validate_csrf(csrf_token)
        subject = self.verify_jwt(request)
        new_token = self.encode_jwt(subject)
        return new_token
        