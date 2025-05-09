# src/services/vector_search_service.py

from typing import Any, Dict, List
from urllib.parse import urlparse

from utils.chroma_client import get_collection
from prompts.query_db_prompt import build_query_db_prompt

def query_top_chunks(
    route: str,
    psi_data: Dict[str, Any],
    collection_name: str = "sitesync",
    top_k: int = 5
) -> List[Dict[str, Any]]:
    # 1) build our natural‑language query
    query_text = build_query_db_prompt(route, psi_data)

    # 2) normalize the URL path into a route_hint
    parsed = urlparse(route)
    route_path = parsed.path or "/"
    if route_path != "/" and route_path.endswith("/"):
        route_path = route_path.rstrip("/")

    col = get_collection(collection_name)

    # 3) first attempt: only chunks with matching route_hint
    res = col.query(
        query_texts=[query_text],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
        where={"route_hint": route_path},
    )

    # 4) if no results, do a global search
    if not res["documents"][0]:
        res = col.query(
            query_texts=[query_text],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

    ids        = res["ids"][0]
    docs       = res["documents"][0]
    metadatas  = res["metadatas"][0]
    distances  = res["distances"][0]

    return [
        {
            "id":       ids[i],
            "content":  docs[i],
            "metadata": metadatas[i],
            "distance": distances[i],
        }
        for i in range(len(ids))
    ]
