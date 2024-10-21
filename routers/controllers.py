from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from setting import SessionLocal
from models import Todo
from datetime import datetime

# ルーターを作成
router = APIRouter()

templates = Jinja2Templates(directory="templates")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def read_todos(request: Request, db: Session = Depends(get_db)):
    todos = db.query(Todo).all()
    context = {
        "request": request,
        "todos": todos 
    }
    return templates.TemplateResponse("index.html", context)

@router.get("/add-todo", response_class=HTMLResponse)
async def add_todo_form(request: Request):
    return templates.TemplateResponse("add_todo.html", {"request": request})

@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    deadline: str = Form(...),
    db: Session = Depends(get_db)
):
    # Parse deadline into datetime object
    deadline_dt = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")

    # Create and add new Todo to the database
    new_todo = Todo(title=title, content=content, deadline=deadline_dt)
    db.add(new_todo)
    db.commit()

    # Redirect back to the main Todo list
    return RedirectResponse(url="/", status_code=303)
