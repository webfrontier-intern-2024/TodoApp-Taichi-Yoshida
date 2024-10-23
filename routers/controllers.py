from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from setting import SessionLocal
from models import Todo, Tag, Setting
from datetime import datetime
from . import crud

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
async def read_todos_html(request: Request, db: Session = Depends(get_db)):
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
@router.get("/add-todo", response_class=HTMLResponse)
async def add_todo_form(request: Request, db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    return templates.TemplateResponse("add_todo.html", {"request": request, "tags": tags})

# Tagページのルート
@router.get("/add-tag", response_class=HTMLResponse)
async def add_tag_form(request: Request, db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    return templates.TemplateResponse("add_tag.html", {"request": request, "tags": tags})

######################
##      操作        ##
######################
@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    title: str = Form(...),
    content: str = Form(...),
    deadline: str = Form(...),
    tags: list[int] = Form(default=[]),
    db: Session = Depends(get_db)
):
    deadline_dt = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
    crud.create_todo_with_tags(db, title, content, deadline_dt, tags)
    return RedirectResponse(url="/?message=Todo successfully added", status_code=303)

@router.delete("/delete-todo/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    deleted_todo = crud.delete_todo_with_settings(db, todo_id)
    if not deleted_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"success": True, "todo_id": todo_id}

@router.post("/toggle-done/{todo_id}")
async def toggle_done(todo_id: int, db: Session = Depends(get_db)):
    todo = crud.toggle_todo_done(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"success": True, "message": "Todo status updated", "todo": todo}

@router.post("/add-tag")
async def create_tag(description: str = Form(...), db: Session = Depends(get_db)):
    crud.create_tag(db, description)
    return JSONResponse({"success": True, "message": "Tag successfully added"})

@router.delete("/delete-tag/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    success = crud.delete_tag(db, tag_id)
    print("HIMAHIMAHIMAIMAHIMAHIMA")
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"success": True, "message": "Tag successfully deleted"}