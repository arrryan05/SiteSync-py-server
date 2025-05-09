# src/services/code_analyzer/extract_relevant_files.py

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel

# exactly the extensions we want to index
TEXT_EXTS = {
    ".js", ".ts", ".jsx", ".tsx",
    ".css", ".scss", ".sass", ".less", ".styl",
    ".html",
}

IGNORE_DIRS = {"node_modules", ".git"}

class FileMeta(BaseModel):
    file_path: str
    relative_path: str
    ext: str
    size_bytes: int
    line_count: int
    import_count: int
    dynamic_import_count: int
    route_hint: Optional[str]

def extract_relevant_files(root: str) -> List[FileMeta]:
    root_path = Path(root)
    metas: List[FileMeta] = []

    for path in root_path.rglob("*"):
        # 1) skip any file under node_modules/.git
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue

        rel = path.relative_to(root_path).as_posix()
        ext = path.suffix.lower()

        # 2) include only our whitelist:
        include = False

        # ➤ JS/TS/JSX/TSX only under pages/, src/pages/, src/components/
        if ext in {".js", ".ts", ".jsx", ".tsx"} and (
            rel.startswith("pages/")
            or rel.startswith("src/pages/")
            or rel.startswith("src/components/")
        ):
            include = True

        # ➤ CSS/etc only under src/
        elif ext in {".css", ".scss", ".sass", ".less", ".styl"} and rel.startswith("src/"):
            include = True

        # ➤ HTML anywhere
        elif ext == ".html":
            include = True

        if not include:
            continue

        # 3) read metrics
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            text = ""
        lines = text.splitlines()
        import_count = text.count("import ")
        dyn_import_count = text.count("import(")

        # 4) build route_hint for pages
        route_hint: Optional[str] = None
        if rel.startswith("pages/") or rel.startswith("src/pages/"):
            # strip prefix, extension, and trailing /index
            route = (
                rel
                .removeprefix("src/pages/")
                .removeprefix("pages/")
                .removesuffix(ext)
                .rstrip("/index")
            )
            route_hint = "/" + (route or "")

        metas.append(FileMeta(
            file_path=str(path),
            relative_path=rel,
            ext=ext,
            size_bytes=path.stat().st_size,
            line_count=len(lines),
            import_count=import_count,
            dynamic_import_count=dyn_import_count,
            route_hint=route_hint,
        ))

    return metas
