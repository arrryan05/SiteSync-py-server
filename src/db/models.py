from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import uuid4
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, JSON
from schemas.project import AnalysisInsight

class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    name: Optional[str]
    email: str = Field(index=True, unique=True)
    email_verified: Optional[datetime] = None
    image: Optional[str] = None
    hashed_password: Optional[str] = None

    # back‑refs
    projects: List["Project"] = Relationship(back_populates="user")


class Project(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    name: Optional[str]
    website: str
    git_url: Optional[str] = None
    analysis: List[AnalysisInsight] = Field(
        sa_column=Column(
            JSON, 
            nullable=False,
            server_default="[]"
        ),
        default_factory=list,
    )

    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    user_id: str = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="projects")
