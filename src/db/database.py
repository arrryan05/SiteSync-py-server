# # src/db/database.py
# import os
# from sqlmodel import SQLModel, create_engine, Session
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker

# # ── 1/ Read your DATABASE_URL from env ────────────────────────────────────────
# DATABASE_URL = os.getenv("DATABASE_URL", "")
# if not DATABASE_URL:
#     raise RuntimeError("DATABASE_URL must be set in your .env")

# # ── 2/ Build an Async URL for asyncpg if needed ───────────────────────────────
# #    e.g. turn "postgresql://user:pass@host/db" into
# #         "postgresql+asyncpg://user:pass@host/db"
# if DATABASE_URL.startswith("postgresql://"):
#     ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
# else:
#     ASYNC_DATABASE_URL = DATABASE_URL

# # ── 3/ Async engine & session factory for FastAPI endpoints ──────────────────
# async_engine = create_async_engine(
#     ASYNC_DATABASE_URL,
#     echo=True,
#     future=True,
# )
# AsyncSessionLocal = sessionmaker(
#     bind=async_engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
# )

# async def init_db() -> None:
#     """
#     Create all tables on startup (async).
#     """
#     import db.models  # noqa: F401 — ensure your SQLModel models are imported
#     async with async_engine.begin() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)

# async def get_session() -> AsyncSession:
#     """
#     Dependency for async routes: yields an AsyncSession.
#     """
#     async with AsyncSessionLocal() as session:
#         try:
#             yield session
#             await session.commit()
#         except:
#             await session.rollback()
#             raise

# # ── 4/ Sync engine & session factory for RQ / one‑off scripts ───────────────
# sync_engine = create_engine(
#     DATABASE_URL,
#     echo=True,
#     future=True,
# )
# SessionLocal = sessionmaker(
#     bind=sync_engine,
#     class_=Session,
#     expire_on_commit=False,
# )

# def get_sync_session() -> Session:
#     """
#     A simple sync session generator for background tasks.
#     """
#     session = SessionLocal()
#     try:
#         yield session
#         session.commit()
#     except:
#         session.rollback()
#         raise
#     finally:
#         session.close()


import os
from contextlib import contextmanager
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# read the single DATABASE_URL:
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set in your .env")

# build the async URL:
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# — your existing async engine/session for FastAPI endpoints —
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        
async def init_db() -> None:
    """
    Create all tables on startup (async).
    """
    import db.models  # noqa: F401 — ensure your SQLModel models are imported
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# — now build a _true sync_ URL for RQ workers — 
# strip "+asyncpg" if present
SYNC_DATABASE_URL = (
    DATABASE_URL 
    if DATABASE_URL.startswith("postgresql://") 
    else DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
)

sync_engine = create_engine(SYNC_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=sync_engine, class_=Session, expire_on_commit=False)

@contextmanager
def get_sync_session() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
