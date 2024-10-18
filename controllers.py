from fastapi import FastAPI, Request, Form, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from models import *
from db import get_db
from datetime import datetime

app = FastAPI()
security = HTTPBasic()

# Todoを追加する関数
@app.post("/todos/add")
async def add_todo(request: Request, 
                   content: str = Form(...), 
                   deadline: str = Form(...), 
                   credentials: HTTPBasicCredentials = Depends(security),
                   db: Session = Depends(get_db)):
    
    # 期限の文字列をdatetimeに変換
    deadline_dt = datetime.strptime(deadline, '%Y-%m-%d_%H:%M:%S')
    
    # 新しいTodoを作成して追加
    new_todo = Todo(content=content, deadline=deadline_dt)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    
    return {"message": "Todoが追加されました", "todo": str(new_todo)}

# Todoを削除する関数
@app.delete("/todos/delete/{todo_id}")
def delete_todo(todo_id: int, 
                credentials: HTTPBasicCredentials = Depends(security), 
                db: Session = Depends(get_db)):    
    # Todoを取得
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if todo:
        # Todoを削除
        db.delete(todo)
        db.commit()
        return {"message": f"Todo {todo_id} が削除されました"}
    
    return {"error": f"Todo {todo_id} が見つかりません"}

# Todoを更新する関数
@app.put("/todos/update/{todo_id}")
async def update_todo(todo_id: int, 
                      content: str = Form(None), 
                      deadline: str = Form(None), 
                      credentials: HTTPBasicCredentials = Depends(security),
                      db: Session = Depends(get_db)):
    
    # Todoを取得
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if not todo:
        return {"error": f"Todo {todo_id} が見つかりません"}
    
    # contentが提供された場合は更新
    if content:
        todo.content = content
    
    # deadlineが提供された場合は更新
    if deadline:
        todo.deadline = datetime.strptime(deadline, '%Y-%m-%d_%H:%M:%S')
    
    db.commit()
    db.refresh(todo)
    
    return {"message": f"Todo {todo_id} が更新されました", "todo": str(todo)}
