from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from setting import SessionLocal
from models import Todo, Tag, Setting
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# データベースセッションを取得する関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def read_todos(request: Request, db: Session = Depends(get_db)):
    # Todoごとに関連する全てのSettingエントリを取得
    todos = db.query(Todo).all()

    # SettingテーブルからTodoに関連するtag_idを使い、Tagテーブルからdescriptionを取得してリスト化
    todos_with_tags = [
        {
            "todo": todo,
            "tags": [
                db.query(Tag.description).filter(Tag.id == setting.tag_id).scalar() 
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

@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    deadline: str = Form(...),
    tags: list[int] = Form(None),  # List of tag IDs (optional)
    db: Session = Depends(get_db)
):
    try:
        deadline_dt = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
        new_todo = Todo(title=title, content=content, deadline=deadline_dt)
        db.add(new_todo)
        db.flush()

        if not tags:
            db.add(Setting(todo_id=new_todo.id, tag_id=None))
        else:
            for tag_id in tags:
                db.add(Setting(todo_id=new_todo.id, tag_id=tag_id))

        db.commit()
        return RedirectResponse(url="/?message=Todo successfully added", status_code=303)

    except Exception as e:
        print(f"Error: {e}")  # ログにエラーメッセージを表示
        return RedirectResponse(url="/?message=Error occurred while adding Todo", status_code=303)

@router.post("/delete-todo/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo:
        db.query(Setting).filter(Setting.todo_id == todo.id).delete()
        db.delete(todo)
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@router.post("/toggle-done/{todo_id}")
async def toggle_done(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo:
        # 型キャストでbool値を取得して反転
        todo.done = not bool(todo.done)

        db.commit()
    return RedirectResponse(url="/", status_code=303)



@router.post("/add-tag", response_class=HTMLResponse)
async def create_tag(request: Request, description: str = Form(...), db: Session = Depends(get_db)):
    new_tag = Tag(description=description)
    db.add(new_tag)
    db.commit()
    return RedirectResponse(url="/add-tag", status_code=303)

@router.post("/delete-tag/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag_to_delete = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag_to_delete:
        db.delete(tag_to_delete)
        db.commit()
    return RedirectResponse(url="/add-tag", status_code=303)
