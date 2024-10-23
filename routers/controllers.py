from fastapi import APIRouter, Request, Depends, Form, HTTPException, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from setting import SessionLocal, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from models import Todo, Tag, Setting
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from . import crud, schemas
import logging

# ロガー設定
logger = logging.getLogger(__name__)

# テンプレートとルータ
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# データベースセッションの依存関係
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT生成関数
async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ユーザー認証
async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# 新規ユーザー登録
@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, username=user.username, password=user.password)

# ログイン処理
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user(db, username=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ユーザー登録ページ
@router.get("/", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# ログインページ
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Todo一覧ページ
@router.get("/home", response_class=HTMLResponse)
async def read_todos_html(request: Request, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
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

# Todo追加ページ
@router.get("/todo", response_class=HTMLResponse)
async def add_todo_form(request: Request, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    tags = db.query(Tag).all()
    return templates.TemplateResponse("todo.html", {"request": request, "tags": tags})

# Tag追加ページ
@router.get("/tag", response_class=HTMLResponse)
async def add_tag_form(request: Request, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    tags = db.query(Tag).all()
    return templates.TemplateResponse("tag.html", {"request": request, "tags": tags})

# Todo作成処理
@router.post("/todo")
async def create_todo(request: schemas.TodoCreate, db: Session = Depends(get_db)):
    try:
        new_todo = crud.create_todo_with_tags(db, request.title, request.content, request.deadline, request.tags)
        return {"success": True, "message": "Todo successfully added", "todo": new_todo}
    except Exception as e:
        logger.error(f"Error occurred while creating todo: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Todo削除
@router.delete("/todo/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    deleted_todo = crud.delete_todo_with_settings(db, todo_id)
    if not deleted_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"success": True, "todo_id": todo_id}

# Todo完了状態の切り替え
@router.put("/todo/{todo_id}")
async def toggle_done(todo_id: int, db: Session = Depends(get_db)):
    todo = crud.toggle_todo_done(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"success": True, "message": "Todo status updated", "todo": todo}

# Tag作成処理
@router.post("/tag")
async def create_tag(request: schemas.TagCreateRequest, db: Session = Depends(get_db)):
    try:
        new_tag = crud.create_tag(db, request.description)
        return {"success": True, "message": "Tag successfully added", "tag": new_tag}
    except Exception as e:
        return {"success": False, "message": str(e)}

# Tag削除
@router.delete("/tag/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    success = crud.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"success": True, "message": "Tag successfully deleted"}
