from pydantic import BaseModel, EmailStr

class WorkerBase(BaseModel):
    name: str
    email: EmailStr

class WorkerCreate(WorkerBase):
    password: str

class WorkerOut(WorkerBase):
    id: int
    
    class Config:
        orm_mode = True

class WorkerLogin(BaseModel):
    email: EmailStr
    password: str

class RefreshToken(BaseModel):
    refresh_token: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str