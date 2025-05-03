import json
import asyncio
import os
from redis import Redis
from rq import Queue
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_session
from db.models import Project
from services.analysis_service import analyze_website
# from code_analyzer import analyze_and_store_repo  # your existing code‐chunker

# this is the function RQ will import by name:
def process_project_analysis(project_id: str, website: str, git_url: str | None = None):
    # # 1) optionally clone & chunk your repo into Chroma:
    # if git_url:
    #     analyze_and_store_repo(git_url, collection_name=project_id)

    # 2) run the PSI→Gemini analysis (this returns List[dict])
    insights = asyncio.run(analyze_website(website))

    # 3) progressively write each route’s insight back to Postgres
    sess_gen = get_session()
    session: AsyncSession = next(sess_gen)

    try:
        stmt = select(Project).where(Project.id == project_id)
        proj = session.exec(stmt).one()

        summary = proj.analysis or []
        for route_insight in insights:
            summary.append(route_insight)
            proj.analysis = summary
            session.add(proj)
            session.commit()
            # optional: pub/sub here

        proj.status = "complete"
        session.add(proj)
        session.commit()

    except Exception:
        proj.status = "error"
        session.add(proj)
        session.commit()
        raise

    finally:
        session.close()
        # exhaust the generator
        try: next(sess_gen)
        except StopIteration: pass
