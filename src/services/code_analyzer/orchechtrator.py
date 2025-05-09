# app/code_analyzer/analyze_and_store.py
import shutil, logging
from .clone_repo import clone_repo
from .extract_relevant_files import extract_relevant_files
from .chunk_code import chunk_code
from .store_chunks import store_chunks

logger = logging.getLogger(__name__)

def orchestrator(repo_url: str, collection_name: str):
    repo_path = clone_repo(repo_url)
    try:
        files  = extract_relevant_files(repo_path)
        logger.info(f"🔍 Found {len(files)} files")
        chunks = chunk_code(files)
        logger.info(f"✂️  Split into {len(chunks)} code chunks")

        store_chunks(chunks, collection_name)
    finally:
        shutil.rmtree(repo_path, ignore_errors=True)
        logger.info("🧹 Removed temp repo")
