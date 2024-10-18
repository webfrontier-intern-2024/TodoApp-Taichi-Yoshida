import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .env.local ファイルから環境変数を読み込む
load_dotenv(".env.local")

# 環境変数からデータベースURLを取得
SQLALCHEMY_DATABASE_URL = os.getenv("HIMAZIN_DATABASE_URL")

# 環境変数が設定されていない場合はエラーを発生させる
if SQLALCHEMY_DATABASE_URL is None:
    raise ValueError("DATABASE_URL 環境変数が設定されていません")

# エンジンを作成
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=True,  # SQLクエリのログ出力を有効にする (デバッグ用)
    pool_size=5,  # コネクションプールのサイズ
    max_overflow=10  # プールを超えて許可される追加接続の数
)

# セッションを作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラスを定義
Base = declarative_base()

# セッションのインスタンスを作成する関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 必要に応じて、明示的にテーブル作成を呼び出す場合
def init_db():
    Base.metadata.create_all(bind=engine)
