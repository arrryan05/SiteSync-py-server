from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.project import CreateProjectRequest, ProjectResponse
from services.project import (
    create_project_service,
    get_all_projects_service,
    get_project_details_service,
    delete_project_service,
)
from task import process_project_analysis
from utils.jwt_bearer import get_current_user
from db.database import get_session
from services.route_extractor import extract_all_routes
from redis import Redis
from rq import Queue,Retry
import os



# set up RQ
redis_conn = Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
)
analysis_q = Queue("analysis", connection=redis_conn)

router = APIRouter(prefix="/project", tags=["project"])


@router.post("/create", response_model=ProjectResponse)
async def create_project(
    payload: CreateProjectRequest,
    session: AsyncSession = Depends(get_session),
    user_data: dict = Depends(get_current_user),
):
    # 1️⃣ create the DB record
    project = await create_project_service(payload, user_data["userId"], session)
    
    # enqueue background job, pass git_url if provided
    analysis_q.enqueue(
        process_project_analysis,
        project.id,
        project.website,
        payload.gitUrl,
        job_timeout="600s",    # adjust
        retry=Retry(max=3, interval=[5, 10, 20])
    )

    # # 2️⃣ immediately fire off your route extractor
    # routes = await extract_all_routes(project.website)
    # # print to your logs so you can see it in `docker-compose logs`:
    # print(f"[route-extractor] for {project.website} → {routes}")

    # 3️⃣ return the newly created project as before
    return project


@router.get("/list", response_model=List[ProjectResponse])
async def list_projects(
    session: AsyncSession = Depends(get_session),
    user_data: dict = Depends(get_current_user),
):
    return await get_all_projects_service(user_data["userId"], session)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_details(
    project_id: str,
    session: AsyncSession = Depends(get_session),
    user_data: dict = Depends(get_current_user),
):
    proj = await get_project_details_service(
        project_id, user_data["userId"], session
    )
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    session: AsyncSession = Depends(get_session),
    user_data: dict = Depends(get_current_user),
):
    try:
        await delete_project_service(project_id, user_data["userId"], session)
        return {"success": True}
    except ValueError:
        raise HTTPException(status_code=404, detail="Project not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")
