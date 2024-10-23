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
    done = Column(Boolean, default=False)

# Tag table definition
class Tag(Base):
    __tablename__ = 'tag'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    description = Column(String(256), nullable=False)

# Setting table definition for Todo-Tag relationships
class Setting(Base):
    __tablename__ = 'setting'
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    todo_id = Column(Integer,ForeignKey('todo.id'), nullable=False)
    tag_id = Column(Integer, ForeignKey('tag.id', ondelete='CASCADE'), nullable=True)

if __name__ == "__main__":
    # テーブルを作成する
    Base.metadata.create_all(bind=Engine)
