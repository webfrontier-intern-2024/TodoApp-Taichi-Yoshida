from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from setting import SessionLocal
from models import Todo, Tag, Setting
from . import crud, schemas
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# データベースセッションを取得する関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 共通CRUD操作をハンドリングする関数
def handle_crud_operation(db, crud_func, *args, success_message="Operation successful", error_message="Operation failed"):
    try:
        result = crud_func(db, *args)
        return {"success": True, "message": success_message, "result": result}
    except Exception as e:
        logger.error(f"{error_message}: {e}")
        raise HTTPException(status_code=500, detail=error_message)

# 共通のテンプレートデータを取得する関数
def common_template_data(request, db):
    return {"request": request, "tags": db.query(Tag).all()}

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
@router.get("/todo", response_class=HTMLResponse)
async def add_todo_form(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("todo.html", common_template_data(request, db))

# Tagページのルート
@router.get("/tag", response_class=HTMLResponse)
async def add_tag_form(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("tag.html", common_template_data(request, db))

# Todo作成
@router.post("/todo")
async def create_todo(
    request: schemas.TodoCreate,
    db: Session = Depends(get_db)
):
    return handle_crud_operation(
        db, crud.create_todo_with_tags, request.title, request.content, request.deadline, request.tags,
        success_message="Todo successfully added"
    )

# Todo削除
@router.delete("/todo/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    return handle_crud_operation(
        db, crud.delete_todo_with_settings, todo_id,
        success_message="Todo successfully deleted",
        error_message="Todo not found"
    )

# Todo更新
@router.put("/todo/{todo_id}")
async def toggle_done(todo_id: int, db: Session = Depends(get_db)):
    return handle_crud_operation(
        db, crud.toggle_todo_done, todo_id,
        success_message="Todo status updated",
        error_message="Todo not found"
    )

# Tag作成
@router.post("/tag")
async def create_tag(request: schemas.TagCreateRequest, db: Session = Depends(get_db)):
    return handle_crud_operation(
        db, crud.create_tag, request.description,
        success_message="Tag successfully added"
    )

# Tag削除
@router.delete("/tag/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    return handle_crud_operation(
        db, crud.delete_tag, tag_id,
        success_message="Tag successfully deleted",
        error_message="Tag not found"
    )
