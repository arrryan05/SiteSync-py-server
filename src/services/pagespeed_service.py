# src/services/pagespeed_service.py
import os
import httpx

PAGE_SPEED_API_KEY = os.getenv("PAGESPEED_API_KEY")

async def fetch_pagespeed_insights(url: str) -> dict:
    """
    Call Google PageSpeed Insights v5 for the given URL.
    """
    if not PAGE_SPEED_API_KEY:
        raise RuntimeError("PAGESPEED_API_KEY not set")
    api = (
        "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        f"?url={httpx.utils.quote(url)}"
        f"&category=performance"
        f"&key={PAGE_SPEED_API_KEY}"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(api, timeout=30.0)
        resp.raise_for_status()
        return resp.json()
