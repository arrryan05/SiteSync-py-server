# app/code_analyzer/chunk_code.py
from typing import List, Optional
from pydantic import BaseModel
from .extract_relevant_files import FileMeta

class CodeChunk(BaseModel):
    chunk_id: str
    content: str
    file_path: str
    relative_path: str
    ext: str
    route_hint: Optional[str]
    start_line: int
    end_line: int
    size_bytes: int
    line_count: int
    import_count: int
    dynamic_import_count: int
    tags: List[str]

LINES_PER_CHUNK = 30

def chunk_code(files: List[FileMeta]) -> List[CodeChunk]:
    chunks: List[CodeChunk] = []
    for meta in files:
        try:
            text = open(meta.file_path, "r", encoding="utf-8").read()
        except:
            continue
        lines = text.splitlines()
        total = len(lines)

        for i in range(0, total, LINES_PER_CHUNK):
            slice_lines = lines[i:i+LINES_PER_CHUNK]
            start, end = i+1, min(i+LINES_PER_CHUNK, total)
            cid = meta.relative_path.replace(r"[\W]", "_") + f"-{start}"
            tags = []
            if meta.route_hint:       tags.append(f"route:{meta.route_hint}")
            tags.append(f"ext:{meta.ext.lstrip('.')}")
            if meta.import_count > 5: tags.append("heavy-imports")
            if meta.dynamic_import_count>0: tags.append("code-splitting")

            chunks.append(CodeChunk(
                chunk_id=cid,
                content="\n".join(slice_lines),
                file_path=meta.file_path,
                relative_path=meta.relative_path,
                ext=meta.ext,
                route_hint=meta.route_hint,
                start_line=start,
                end_line=end,
                size_bytes=meta.size_bytes,
                line_count=end-start+1,
                import_count=meta.import_count,
                dynamic_import_count=meta.dynamic_import_count,
                tags=tags,
            ))
    return chunks
