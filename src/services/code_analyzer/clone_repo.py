# app/code_analyzer/clone_repo.py
import os, shutil, tempfile, uuid, subprocess, logging

logger = logging.getLogger(__name__)

def clone_repo(repo_url: str) -> str:
    tmp_root = tempfile.gettempdir()
    out_dir = os.path.join(tmp_root, f"sitesync-repo-{uuid.uuid4()}")
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir, exist_ok=True)

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch", repo_url, out_dir],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        logger.info(f"✅ Cloned {repo_url} → {out_dir}")
        return out_dir
    except subprocess.CalledProcessError as e:
        logger.error(f"Git clone failed: {e.stderr.decode()}")
        shutil.rmtree(out_dir, ignore_errors=True)
        raise
