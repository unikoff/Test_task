import uvicorn
from fastapi import FastAPI

from app.routers.user.user_rt import user_router
from app.routers.task.task_rt import task_router
from app.DBpackage import database

app = FastAPI()
app.include_router(user_router)
app.include_router(task_router)


@app.on_event("startup")
def on_startup():
    # Создает все таблицы, если они еще не созданы
     database.Base.metadata.create_all(bind=database.engine)


# if __name__=="__main__":
#      uvicorn.run(app='main:app', reload=True)     