from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from jose import JWTError, jwt
from typing import Optional

from typing import Optional
from functools import wraps

from app.DBpackage.database import SessionLocal
from . import schemas, crud

SECRET_KEY = "unik" # естественно по правилам он должен быть в .env
ALGORITHM = "HS256"
ACCESS_EXPIRE_MINUTES = 30
REFRESH_EXPIRE_MINUTES = 1440

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")
user_router = APIRouter(prefix="/user", tags=["user"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def jwt_required(func):
    @wraps(func)
    async def wrapper(
        request: Request,
        *args,
        **kwargs
    ):
        # Создаём сессию БД вручную
        db = SessionLocal()
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid Authorization header"
                )
            
            token = auth_header.split(" ", 1)[1]
            email = decode_token(token)
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
            
            user = crud.get_user_by_email(db, email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )


            request.state.db = db
            request.state.user = user

            return await func(request, *args, **kwargs)
        
        finally:
            db.close()
    
    return wrapper

def create_token(data: dict, expires_minutes: int) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        email = decode_token(token)
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

@user_router.post("/register", response_model=schemas.WorkerOut, status_code=201)
def register(worker: schemas.WorkerCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, worker.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = crud.hash_password(worker.password)
    return crud.create_user(db, worker, hashed)

@user_router.post("/login", response_model=schemas.Token)
def login(form_data: schemas.WorkerLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_token({"sub": user.email}, ACCESS_EXPIRE_MINUTES)
    refresh = create_token({"sub": user.email}, REFRESH_EXPIRE_MINUTES)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer"
    }

@user_router.post("/refresh", response_model=schemas.Token)
def refresh(token_data: schemas.RefreshToken, db: Session = Depends(get_db)):
    email = decode_token(token_data.refresh_token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Проверяем существование пользователя
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Здесь можно добавить проверку refresh токена в базе данных
    # для инвалидации использованных токенов
    
    access = create_token({"sub": email}, ACCESS_EXPIRE_MINUTES)
    refresh = create_token({"sub": email}, REFRESH_EXPIRE_MINUTES)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer"
    }


@user_router.get("/me", response_model=schemas.WorkerOut)
@jwt_required
async def read_users_me(request: Request):
    return request.state.user