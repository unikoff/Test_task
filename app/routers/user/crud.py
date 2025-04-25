from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import schemas
from app.DBpackage import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.WorkerCreate, hashed_password: str):
    db_worker = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)
    return db_worker

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)