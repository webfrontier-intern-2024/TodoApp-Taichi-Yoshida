from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN
from sqlalchemy.sql import null
from setting import Engine, Base
from datetime import datetime
from typing import Optional

# Todo table definition
class Todo(Base):
    __tablename__ = 'todo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    content = Column(String(256), nullable=False)
    deadline = Column(DateTime, nullable=False)
    done = Column(BOOLEAN, default=False)

    def __init__(self, title: str, content: str, deadline: datetime):
        self.title = title
        self.content = content
        self.deadline = deadline
        self.done = False

    def __str__(self):
        id_str = str(self.id) if self.id is not None else 'No ID'
        title_str = self.title or 'No Title'
        content_str = self.content or 'No Content'
        deadline_str = self.deadline.strftime('%Y/%m/%d - %H:%M:%S') if isinstance(self.deadline, datetime) else 'No Deadline'
        done_str = str(self.done)
        return f"{id_str}, title -> {title_str}, content -> {content_str}, deadline -> {deadline_str}, done -> {done_str}"

# Tag table definition
class Tag(Base):
    __tablename__ = 'tag'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    description = Column(String(256), nullable=False)

    def __init__(self, description: str):
        self.description = description

    def __str__(self):
        id_str = str(self.id) if self.id is not None else 'No ID'
        description_str = self.description if self.description is not None else 'No Description'
        return f"{id_str}: {description_str}"

# Setting table definition for Todo-Tag relationships
class Setting(Base):
    __tablename__ = 'setting'
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    todo_id = Column(ForeignKey('todo.id'), nullable=False)
    tag_id = Column(ForeignKey('tag.id', ondelete='CASCADE'), nullable=True) 

    def __init__(self, todo_id: int, tag_id:int | None):
        self.todo_id = todo_id
        self.tag_id = tag_id
    def __str__(self):
        return f'Todo番号: {self.todo_id}, Tag番号: {self.tag_id}'

if __name__ == "__main__":
    # テーブルを作成する
    Base.metadata.create_all(bind=Engine)
