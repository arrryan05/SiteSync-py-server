# src/task/process.py

import asyncio
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from db.database import get_sync_session
from db.models import Project
from services.analysis_service import analyze_website

def process_project_analysis(project_id: str,name:str, website: str, gitUrl: str | None = None):
    """
    RQ task: run the full PSI→Gemini pipeline, then update `project.analysis`
    all at once and mark the project complete (or error).
    """
    print(f"[RQ Task] Starting analysis for project_id={project_id}")

    # 1) Run the async analysis pipeline outside of the DB session
    try:
        insights = asyncio.run(analyze_website(website,name,gitUrl))
        print(f"[RQ Task] insights from analyze_website = {insights!r}")
    except Exception as e:  
        print(f"[RQ Task] analyze_website failed for {project_id}: {e}")
        # Optional: mark project as error if you want
        with get_sync_session() as session:
            try:
                proj = session.exec(
                    select(Project).where(Project.id == project_id)
                ).scalar_one()
                proj.status = "error"
                session.add(proj)
                session.commit()
            except NoResultFound:
                pass
        raise

    # 2) Open a purely‑sync session and overwrite the entire analysis list
    with get_sync_session() as session:
        try:
            proj = session.exec(
                select(Project).where(Project.id == project_id)
            ).scalar_one()
        except NoResultFound:
            print(f"[RQ Task] Project {project_id} not found, aborting.")
            return

        # 3) Overwrite `analysis` with the full list of insights
        proj.analysis = insights

        # 4) Mark as complete
        proj.status = "complete"

        # 5) Persist both fields in one go
        session.add(proj)
        session.commit()

    print(f"[RQ Task] Finished analysis for project_id={project_id}")
