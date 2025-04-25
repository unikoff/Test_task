from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, example="Fix login bug")
    description: Optional[str] = Field(
        None, max_length=500, example="Critical authentication issue"
    )
    status: str = Field(default="todo", example="in_progress")
    priority: str = Field(default="medium", example="high")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None, min_length=3, max_length=100, 
        example="New task title"
    )
    description: Optional[str] = Field(
        None, max_length=500, 
        example="Updated description"
    )
    status: Optional[str] = Field(
        None, pattern="^(todo|in_progress|done)$",
        example="in_progress"
    )
    priority: Optional[str] = Field(
        None, pattern="^(low|medium|high)$",
        example="high"
    )

    @field_validator('*', mode='before')
    def remove_blank_strings(cls, v):
        return None if v == "" else v

class TaskOut(TaskBase):
    id: int
    created_at: datetime
    user_id: int
    
    class Config:
        from_attributes = True