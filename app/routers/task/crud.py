from sqlalchemy.orm import Session
from app.DBpackage import models

def create_task(db: Session, task_data: dict, user_id: int):
    db_task = models.Task(**task_data, user_id=user_id)  # Добавляем user_id
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, update_data: dict, user_id: int):
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == user_id
    ).first()
    
    if not db_task:
        return None
    
    # Обновляем только переданные поля
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, status: str = None, priority: str = None, created_at: str = None):
    query = db.query(models.Task)
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    if created_at:
        query = query.filter(models.Task.created_at >= created_at)
    return query.all()

def search_tasks(db: Session, search_term: str):
    return db.query(models.Task).filter(
        (models.Task.title.ilike(f"%{search_term}%")) | 
        (models.Task.description.ilike(f"%{search_term}%"))
    ).all()