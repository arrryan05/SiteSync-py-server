# import json
# import asyncio
# import os
# from redis import Redis
# from rq import Queue
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from db.database import get_session
# from db.models import Project
# from services.analysis_service import analyze_website

# # this is the function RQ will import by name:
# def process_project_analysis(project_id: str, website: str, git_url: str | None = None):
#     print(f"[RQ Task] Running analysis for project_id={project_id}")
#     # # 1) optionally clone & chunk your repo into Chroma:
#     # if git_url:
#     #     analyze_and_store_repo(git_url, collection_name=project_id)

#     # 2) run the PSI→Gemini analysis (this returns List[dict])
#     insights = asyncio.run(analyze_website(website))

#     # 3) progressively write each route’s insight back to Postgres
#     sess_gen = get_session()
#     session: AsyncSession = next(sess_gen)

#     try:
#         stmt = select(Project).where(Project.id == project_id)
#         proj = session.exec(stmt).one()

#         summary = proj.analysis or []
#         for route_insight in insights:
#             summary.append(route_insight)
#             proj.analysis = summary
#             session.add(proj)
#             session.commit()
#             # optional: pub/sub here

#         proj.status = "complete"
#         session.add(proj)
#         session.commit()

#     except Exception:
#         proj.status = "error"
#         session.add(proj)
#         session.commit()
#         raise

#     finally:
#         session.close()
#         # exhaust the generator
#         try: next(sess_gen)
#         except StopIteration: pass


# src/task.py

import asyncio
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from db.database import get_sync_session
from db.models import Project
from services.analysis_service import analyze_website

def process_project_analysis(project_id: str, website: str, git_url: str | None = None):
    """
    RQ task: run the full PSI→Gemini pipeline, then update `project.analysis`
    all at once and mark the project complete (or error).
    """
    print(f"[RQ Task] Starting analysis for project_id={project_id}")

    # 1) Run the async analysis pipeline outside of the DB session
    try:
        insights = asyncio.run(analyze_website(website))
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
