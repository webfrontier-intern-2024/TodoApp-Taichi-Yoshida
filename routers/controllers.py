from fastapi import APIRouter, Request, Depends, Form, HTTPException,Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from setting import SessionLocal
from models import Todo, Tag, Setting
from datetime import datetime
from . import crud,schemas

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# データベースセッションを取得する関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Todo一覧のページ
@router.get("/", response_class=HTMLResponse)
async def read_todos_html(request: Request, db: Session = Depends(get_db),skip: int = 0, limit: int = 100):
    todos = db.query(Todo).all()
    todos_with_tags = [
        {
            "todo": todo,
            "tags": [
                tag.description if (tag := db.query(Tag).filter(Tag.id == setting.tag_id).first()) is not None else ""
                for setting in db.query(Setting).filter(Setting.todo_id == todo.id).all()
            ]
        }
        for todo in todos
    ]
    return templates.TemplateResponse("index.html", {"request": request, "todos_with_tags": todos_with_tags})

# Todo追加ページのルート
@router.get("/todo", response_class=HTMLResponse)
async def add_todo_form(request: Request, db: Session = Depends(get_db),skip: int = 0, limit: int = 100):
    tags = db.query(Tag).all()
    return templates.TemplateResponse("todo.html", {"request": request, "tags": tags})

# Tagページのルート
@router.get("/tag", response_class=HTMLResponse)
async def add_tag_form(request: Request, db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    tags = db.query(Tag).all()
    return templates.TemplateResponse("tag.html", {"request": request, "tags": tags})

######################
##      操作        ##
######################
@router.post("/todo")
async def create_todo(
    request: schemas.TodoCreate,  # JSONリクエストボディを受け取る
    db: Session = Depends(get_db)
):
    deadline_dt = request.deadline, "%Y-%m-%dT%H:%M")
    new_todo = crud.create_todo_with_tags(db, request.title, request.content, deadline_dt, request.tags)
    return {"success": True, "message": "Todo successfully added", "todo": new_todo}

@router.delete("/todo/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    deleted_todo = crud.delete_todo_with_settings(db, todo_id)
    if not deleted_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"success": True, "todo_id": todo_id}

@router.put("/todo/{todo_id}")
async def toggle_done(todo_id: int, db: Session = Depends(get_db)):
    todo = crud.toggle_todo_done(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"success": True, "message": "Todo status updated", "todo": todo}

@router.post("/tag")
async def create_tag(request: schemas.TagCreateRequest, db: Session = Depends(get_db)):
    try:
        new_tag = crud.create_tag(db, request.description)
        return {"success": True, "message": "Tag successfully added", "tag": new_tag}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.delete("/tag/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    success = crud.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"success": True, "message": "Tag successfully deleted"}