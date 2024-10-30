from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from setting import SessionLocal
from models import Todo, Tag, Setting
from . import crud, schemas

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# データベースセッションを取得する関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 共通のテンプレートデータを取得する関数
def common_template_data(request, db):
    return {"request": request, "tags": db.query(Tag).all()}

# Todo一覧のページ
@router.get("/", response_class=HTMLResponse)
async def read_todos_html(request: Request, db: Session = Depends(get_db)):
    todos = db.query(Todo).all()
    todos_with_tags = crud.get_todos_with_tags(db)
    return templates.TemplateResponse("index.html", {"request": request, "todos_with_tags": todos_with_tags})

# Todo追加ページのルート
@router.get("/todo", response_class=HTMLResponse)
async def add_todo_form(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("todo.html", common_template_data(request, db))

# Tagページのルート
@router.get("/tag", response_class=HTMLResponse)
async def add_tag_form(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("tag.html", common_template_data(request, db))

# # Todo一覧取得
# @router.get("/todos", response_class=JSONResponse)
# async def read_todos_json(db: Session = Depends(get_db)):
#     todos_with_tags = crud.get_todos_with_tags(db)
#     return {"todos": todos_with_tags}

# Todo作成
@router.post("/todo")
async def create_todo(
    request: schemas.TodoCreate,
    db: Session = Depends(get_db)
):
    try:
        result = crud.create_todo_with_tags(db, request.title, request.content, request.deadline, request.tags)
        return {"success": True, "message": "Todo successfully added", "todo_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to add Todo")

# Todo削除
@router.delete("/todo/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_todo_with_settings(db, todo_id)  # Assuming this function does not return a value
        return {"success": True, "message": "Todo successfully deleted", "todo_id": todo_id}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Todo not found")

# TodoDone更新
@router.put("/todo/done/{todo_id}")
async def toggle_done(todo_id: int, db: Session = Depends(get_db)):
    try:
        crud.toggle_todo_done(db, todo_id)  # Assuming this function does not return a value
        return {"success": True, "message": "Todo status updated", "todo_id": todo_id}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Todo not found")

# Todo更新
@router.put("/todo/{todo_id}")
async def update_todo(
    todo_id: int,
    request: schemas.TodoUpdate,  # 新しいスキーマを追加する必要があります
    db: Session = Depends(get_db)
):
    try:
        # Todoの情報を更新するCRUD関数を呼び出す
        updated_todo = crud.update_todo_with_tags(db, todo_id, request.title, request.content, request.deadline, request.tags)
        if updated_todo:
            return {"success": True, "message": "Todo successfully updated", "todo_id": updated_todo.id}
        else:
            raise HTTPException(status_code=404, detail="Todo not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update Todo")

# # Tag一覧取得
# @router.get("/tags", response_class=JSONResponse)
# async def read_tags_json(db: Session = Depends(get_db)):
#     tags = crud.get_all_tags(db)
#     return {"tags": [tag.description for tag in tags]}

# Tag作成
@router.post("/tag")
async def create_tag(request: schemas.TagCreateRequest, db: Session = Depends(get_db)):
    try:
        result = crud.create_tag(db, request.description)
        return {"success": True, "message": "Tag successfully added", "tag_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to add Tag")

# Tag削除
@router.delete("/tag/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_tag(db, tag_id)  # Assuming this function does not return a value
        return {"success": True, "message": "Tag successfully deleted", "tag_id": tag_id}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Tag not found")
