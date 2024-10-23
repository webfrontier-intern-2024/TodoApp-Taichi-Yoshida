from sqlalchemy.orm import Session
from models import Todo, Tag, Setting

def create_todo_with_tags(db: Session, title: str, content: str, deadline, tags: list[int]):
    new_todo = Todo(title=title, content=content, deadline=deadline)
    db.add(new_todo)
    db.commit() 
    for tag_id in tags:
        db.add(Setting(todo_id=new_todo.id, tag_id=tag_id))
    db.commit()
    return new_todo  # Return the new todo

def delete_todo_with_settings(db: Session, todo_id: int):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo:
        db.query(Setting).filter(Setting.todo_id == todo_id).delete()
        db.delete(todo)
        db.commit()
        return todo
    return None

def toggle_todo_done(db: Session, todo_id: int):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo:
        todo.done = not bool(todo.done)
        db.commit()
        return {
            "success": True,
            "todo": {
                "id": todo.id,
                "done": todo.done,
                "title": todo.title,
            }
        }
    return {"success": False, "message": "Todo not found"}

def create_tag(db: Session, description: str):
    new_tag = Tag(description=description)
    db.add(new_tag)
    db.commit()
    return new_tag

def delete_tag(db: Session, tag_id: int):
    # 関連する設定（Settings）の削除
    db.query(Setting).filter(Setting.tag_id == tag_id).delete()
    # タグ自体の削除
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
        return True

    # コミットを追加
    db.commit()
    return None
