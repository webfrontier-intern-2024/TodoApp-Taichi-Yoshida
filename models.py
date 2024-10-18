from datetime import datetime
from db import Base
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN

class Todo(Base):
    """
    Todoテーブル

    id       : Todo番号 (主キー)
    content  : 内容
    deadline : 期限
    done     : 完了・未完了
    """
    __tablename__ = 'todo'
    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )
    content = Column('content', String(256))
    deadline = Column(
        'deadline',
        DateTime,
        default=None,
        nullable=False,
    )
    done = Column('done', BOOLEAN, default=False, nullable=False)

    def __init__(self, content: str, deadline: datetime):
        self.content = content
        self.deadline = deadline
        self.done = False

def __str__(self):
    # 各カラムの値を取得し、None チェックを行う
    id_str = str(self.id) if self.id is not None else 'No ID'
    content_str = self.content if self.content else 'No Content'
    
    # deadlineがNoneでない場合にstrftimeを呼び出す
    deadline_str = self.deadline.strftime('%Y/%m/%d - %H:%M:%S') if isinstance(self.deadline, datetime) else 'No Deadline'
    done_str = str(self.done)

    return f"{id_str}, content -> {content_str}, deadline -> {deadline_str}, done -> {done_str}"


# Tag table definition
class Tag(Base):
    """
    Tagテーブル

    id         : Tag番号 (主キー)
    description: 説明
    """
    __tablename__ = 'tag'
    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )
    description = Column('description', String(256))

    def __init__(self, description: str):
        self.description = description

    def __str__(self):
        # id が None の場合のチェック
        id_str = str(self.id) if self.id is not None else 'No ID'
        
        # description が None の場合のチェック
        description_str = self.description if self.description is not None else 'No Description'

        return f"{id_str}: {description_str}"

# Setting table definition for Todo-Tag relationships
class Setting(Base):
    """
    Settingテーブル (TodoとTagの多対多関係)

    id       : 主キー
    todo_id  : Todo番号 (外部キー)
    tag_id   : Tag番号 (外部キー)
    """
    __tablename__ = 'setting'
    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )
    todo_id = Column('todo_id', ForeignKey('todo.id'), nullable=False)
    tag_id = Column('tag_id', ForeignKey('tag.id'), nullable=False)

    def __init__(self, todo_id: int, tag_id: int):
        self.todo_id = todo_id
        self.tag_id = tag_id

    def __str__(self):
        return 'Todo番号: ' + str(self.todo_id) + ', Tag番号: ' + str(self.tag_id)
