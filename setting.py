import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

# .env.local ファイルから環境変数を読み込む
load_dotenv(".env.local")

SECRET_KEY = os.getenv("SECRET_KEY") or "your_secret_key"  # Store in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# パスワードのハッシュ化設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# PostgreSQL接続情報の設定
DATABASE = os.getenv("HIMAZIN_DATABASE_URL")

if DATABASE is None:
    print("Error: Database URL not set in environment variables")
    sys.exit(1)  # エラー終了

# Engineの作成
Engine = create_engine(
    DATABASE,
    echo=False  # ログを出力しない場合はFalse
)

# Baseクラスの定義
Base = declarative_base()

# sessionmakerの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

# 必要なときにセッションを使う
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()