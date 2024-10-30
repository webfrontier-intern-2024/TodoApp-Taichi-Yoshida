from sqlalchemy.orm import Session
from models import Todo, Tag, Setting
from datetime import datetime
from typing import Optional

def get_todos_with_tags(db: Session, skip: int = 0, limit: int = 100):
    todos = db.query(Todo).offset(skip).limit(limit).all()
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
    print("Todos with tags constructed:", todos_with_tags)  # デバッグ用ログ
    return todos_with_tags

def create_todo_with_tags(db: Session, title: str, content: str, deadline, tags: list[int]):
    try:
        new_todo = Todo(title=title, content=content, deadline=deadline)
        db.add(new_todo)
        db.flush()
        settings = [Setting(todo_id=new_todo.id, tag_id=tag_id) for tag_id in tags]
        db.bulk_save_objects(settings)
        db.commit()
        db.refresh(new_todo)
        return new_todo
    except Exception as e:
        db.rollback()
        raise

def delete_todo_with_settings(db: Session, todo_id: int):
    try:
        todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if todo:
            db.query(Setting).filter(Setting.todo_id == todo_id).delete()
            db.delete(todo)
            db.commit()
            return todo
        return None
    except Exception as e:
        db.rollback()
        raise

def toggle_todo_done(db: Session, todo_id: int):
    try:
        todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if todo:
            todo.done = not todo.done
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
    except Exception as e:
        db.rollback()
        raise

def update_todo_with_tags(db: Session, todo_id: int, title: str, content: str, deadline: Optional[datetime], tags: list[int]):
    try:
        todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if todo:
            todo.title = title
            todo.content = content
            todo.deadline = deadline  # datetime型として直接代入

            # 既存の設定を削除
            db.query(Setting).filter(Setting.todo_id == todo_id).delete()

            # 新しい設定を追加
            settings = [Setting(todo_id=todo_id, tag_id=tag_id) for tag_id in tags]
            db.bulk_save_objects(settings)

            db.commit()
            db.refresh(todo)
            return todo
        return None
    except Exception as e:
        db.rollback()
        raise


def get_all_tags(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Tag).offset(skip).limit(limit).all()

def create_tag(db: Session, description: str):
    try:
        new_tag = Tag(description=description)
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return new_tag
    except Exception as e:
        db.rollback()
        raise

def delete_tag(db: Session, tag_id: int):
    try:
        # タグが存在するか確認
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if tag:
            # 関連するSettingの削除
            db.query(Setting).filter(Setting.tag_id == tag_id).delete()
            db.delete(tag)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise

