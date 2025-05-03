# from fastapi import FastAPI
# from db.database import engine
# from sqlmodel import SQLModel
# from controllers.auth import router as auth_router
# from controllers.project import router as project_router

# import db.models  # ensure models are registered

# app = FastAPI()

# @app.on_event("startup")
# def on_startup():
#     SQLModel.metadata.create_all(engine)

# app.include_router(auth_router)
# app.include_router(project_router)

from fastapi import FastAPI

from db.database import init_db
from controllers.auth import router as auth_router
from controllers.project import router as project_router

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(auth_router)
app.include_router(project_router)
