from fastapi import APIRouter, HTTPException, Request
from . import schemas, crud
from app.routers.user.user_rt import jwt_required

task_router = APIRouter(prefix="/tasks", tags=["tasks"])

@task_router.post("", response_model=schemas.TaskOut)
@jwt_required
async def create_task(request: Request, task_data: schemas.TaskCreate):
    db = request.state.db
    user = request.state.user
    
    return crud.create_task(db=db, task_data=task_data.dict(), user_id=user.id)

@task_router.put("/{task_id}", response_model=schemas.TaskOut)
@jwt_required
async def update_task(
    request: Request,
    task_id: int,
    task_data: schemas.TaskUpdate
):
    db = request.state.db
    user = request.state.user
    
    # Фильтруем None значения
    update_data = task_data.model_dump(exclude_unset=True)
    
    task = crud.update_task(
        db=db,
        task_id=task_id,
        update_data=update_data,
        user_id=user.id
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@task_router.get("", response_model=list[schemas.TaskOut])
@jwt_required
async def get_tasks(
    request: Request,
    status: str = None,
    priority: str = None,
    created_at: str = None
):
    db = request.state.db
    return crud.get_tasks(db, status, priority, created_at)

@task_router.get("/search", response_model=list[schemas.TaskOut])
@jwt_required
async def search_tasks(request: Request, q: str):
    db = request.state.db
    return crud.search_tasks(db, q)