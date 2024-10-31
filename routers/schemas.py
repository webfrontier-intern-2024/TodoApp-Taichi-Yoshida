from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TodoBase(BaseModel):
    title: str
    content: str
    deadline: datetime
    done: Optional[bool] = False

class TodoCreate(TodoBase):
    tags: List[int] = []

class TodoResponse(TodoBase):
    id: int

class TagResponse(BaseModel):
    id: int
    description: str

class SuccessResponse(BaseModel):
    success: bool
    message: Optional[str] = None
class TagCreateRequest(BaseModel):
    description: str

class TodoUpdateRequest(BaseModel):
    title: str
    content: str
    date: str

class TodoUpdate(BaseModel):
    title: str
    content: str
    deadline: datetime
    tags: List[int] = []