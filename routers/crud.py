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
        db.query(Setting).filter(Setting.todo_id == todo.id).delete()
        db.delete(todo)
        db.commit()
        return todo  # Return the deleted todo
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
                "title": todo.title,  # 必要なフィールドを追加
                # 他のフィールドも追加可能
            }
        }
    return {"success": False, "message": "Todo not found"}

def create_tag(db: Session, description: str):
    new_tag = Tag(description=description)
    db.add(new_tag)
    db.commit()
    return new_tag  # Return the new tag

def delete_tag(db: Session, tag_id: int):
    tag_to_delete = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag_to_delete:
        db.delete(tag_to_delete)
        db.commit()
        return tag_to_delete  # Return the deleted tag
    return None
