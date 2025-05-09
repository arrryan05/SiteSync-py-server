# app/code_analyzer/store_chunks.py
from utils.chroma_client import get_collection
from .chunk_code import CodeChunk
import logging

logger = logging.getLogger(__name__)

def store_chunks(chunks: list[CodeChunk], collection_name: str):
    col = get_collection(collection_name)

    # 1️⃣ Build your full lists
    ids   = [c.chunk_id     for c in chunks]
    docs  = [c.content      for c in chunks]
    metas = [
        {
            "file_path":     c.file_path,
            "relative_path": c.relative_path,
            "ext":            c.ext,
            "route_hint":     c.route_hint or "",
            "tags":           ",".join(c.tags),
            "start_line":     c.start_line,
            "end_line":       c.end_line,
        }
        for c in chunks
    ]

    # 2️⃣ Decide your batch size
    # You can use Chroma’s max_batch_size if you want to
    try:
        max_batch = col._client.max_batch_size  # SQLite driver limit
    except AttributeError:
        max_batch = 50                           # fallback

    # 3️⃣ Slice & upload each batch
    for i in range(0, len(ids), max_batch):
        batch_ids   = ids[i : i + max_batch]
        batch_docs  = docs[i : i + max_batch]
        batch_metas = metas[i : i + max_batch]

        # DEBUG: ensure every metadata is a dict
        for md in batch_metas:
            if not isinstance(md, dict):
                logger.error("Bad metadata entry (not a dict!): %r", md)
                raise ValueError(f"Found non‐dict metadata: {type(md)}")

        logger.info(f"Storing batch {i//max_batch + 1} ({len(batch_ids)} items)…")
        col.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_metas,
        )

    logger.info(f"✅ All {len(ids)} chunks stored in '{collection_name}'")


