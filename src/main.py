from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import init_db
from controllers.auth import router as auth_router
from controllers.project import router as project_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # <-- React/Next dev server
    allow_credentials=True,
    allow_methods=["*"],                      # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],                      # Authorization, Content-Type, etc.
)

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(auth_router)
app.include_router(project_router)
