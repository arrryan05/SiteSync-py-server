# src/utils/concurrency.py
import asyncio
from typing import Any, Callable, List, Optional

async def run_with_concurrency(
    items: List[Any],
    concurrency: int,
    fn: Callable[[Any], Any],
) -> List[Optional[Any]]:
    """
    Fire off at most `concurrency` simultaneous tasks over `items`.
    Returns list of results or None on error.
    """
    results: List[Optional[Any]] = [None] * len(items)
    sem = asyncio.Semaphore(concurrency)

    async def worker(i: int, item: Any):
        async with sem:
            try:
                results[i] = await fn(item)
            except Exception:
                results[i] = None

    await asyncio.gather(*(worker(i, it) for i, it in enumerate(items)))
    return results
