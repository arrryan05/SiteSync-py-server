# app/services/project.py

from uuid import uuid4
from datetime import datetime
from typing import List, Optional, Union

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Project
from schemas.project import CreateProjectRequest, ProjectResponse, AnalysisInsight


async def create_project_service(
    payload: CreateProjectRequest,
    user_id: str,
    session: AsyncSession,
) -> ProjectResponse:
    project = Project(
        id=str(uuid4()),
        website=payload.website,
        name=payload.name,
        git_url=payload.gitUrl,
        status="pending",
        analysis=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        user_id=user_id,
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)

    return ProjectResponse(
        id=project.id,
        website=project.website,
        name=project.name,
        gitUrl=project.git_url,
        status=project.status,
        analysisSummary=project.analysis or [],
        createdAt=project.created_at,
        updatedAt=project.updated_at,
    )


async def get_all_projects_service(
    user_id: str,
    session: AsyncSession
) -> List[ProjectResponse]:
    stmt = (
        select(Project)
        .where(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
    )
    result = await session.execute(stmt)
    projects = result.scalars().all()

    responses: List[ProjectResponse] = []
    for p in projects:
        # Filter out any None entries in the analysis list
        filtered_analysis: List[AnalysisInsight] = [
            ins for ins in (p.analysis or []) if ins is not None
        ]
        responses.append(
            ProjectResponse(
                id=p.id,
                website=p.website,
                name=p.name,
                gitUrl=p.git_url,
                status=p.status,
                analysisSummary=filtered_analysis,
                createdAt=p.created_at,
                updatedAt=p.updated_at,
            )
        )
    return responses


async def get_project_details_service(
    project_id: str,
    user_id: str,
    session: AsyncSession
) -> Optional[ProjectResponse]:
    stmt = select(Project).where(Project.id == project_id)
    result = await session.execute(stmt)
    project = result.scalar_one_or_none()

    if not project or project.user_id != user_id:
        return None

    # Filter out any None entries in the analysis list
    filtered_analysis: List[AnalysisInsight] = [
        ins for ins in (project.analysis or []) if ins is not None
    ]

    return ProjectResponse(
        id=project.id,
        website=project.website,
        name=project.name,
        gitUrl=project.git_url,
        status=project.status,
        analysisSummary=filtered_analysis,
        createdAt=project.created_at,
        updatedAt=project.updated_at,
    )


async def delete_project_service(
    project_id: str,
    user_id: str,
    session: AsyncSession
) -> None:
    stmt = select(Project).where(Project.id == project_id)
    result = await session.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise ValueError("Project not found")
    if project.user_id != user_id:
        raise PermissionError("Not authorized")

    await session.delete(project)
    await session.commit()
