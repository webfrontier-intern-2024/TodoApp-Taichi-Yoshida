import os
from datetime import datetime  # datetimeのインポートを追加
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Todo  # 必要なモデルをインポート

# .env.localファイルから環境変数を読み込む
load_dotenv(".env.local")

# 環境変数からデータベースURLを取得
SQLALCHEMY_DATABASE_URL = os.getenv("HIMAZIN_DATABASE_URL")

# 環境変数が設定されていない場合はエラーを発生させる
if SQLALCHEMY_DATABASE_URL is None:
    raise ValueError("HIMAZIN_DATABASE_URL 環境変数が設定されていません")

# エンジンを作成
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def insert_test_data():
    # セッションを作成
    db = SessionLocal()
    try:
        # テストデータの作成
        todo1 = Todo(title="買い物", content="牛乳を買う", deadline=datetime(2024, 10, 20, 12, 0))
        todo2 = Todo(title="勉強", content="Pythonを勉強する", deadline=datetime(2024, 10, 21, 18, 0))

        # データベースに追加
        db.add(todo1)
        db.add(todo2)
        db.commit()

        # 確認のためにDBから取得
        todos = db.query(Todo).all()
        for todo in todos:
            print(todo)
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        db.rollback()  # エラーが発生した場合、ロールバックする
    finally:
        db.close()

if __name__ == "__main__":
    insert_test_data()
