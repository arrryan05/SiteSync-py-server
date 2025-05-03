# from fastapi import FastAPI, Depends
# from sqlmodel import Session
# from db.database import init_db, SessionLocal
# import db.models  # noqa: F401  (import models so metadata exists)

# app = FastAPI()

# # Create tables on startup (for dev; use Alembic in prod)
# @app.on_event("startup")
# def on_startup():
#     init_db()

# # Dependency that provides a DB session per request
# def get_session():
#     with SessionLocal() as session:
#         yield session 

# @app.get("/")
# def read_root():
#     return {"message": "Hello, FastAPI + Postgres!"}

# # Example endpoint using the session
# @app.get("/users")
# def list_users(session: Session = Depends(get_session)):
#     users = session.exec(db.models.User.select()).all()
#     return users

from fastapi import FastAPI
from db.database import engine
from sqlmodel import SQLModel
from controllers.auth import router as auth_router
import db.models  # ensure models are registered

app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

app.include_router(auth_router)

