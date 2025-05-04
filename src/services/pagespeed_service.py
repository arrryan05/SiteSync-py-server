# src/services/pagespeed_service.py
import os
import httpx
from urllib.parse import quote

PAGE_SPEED_API_KEY = os.getenv("PAGE_SPEED_API_KEY")

async def fetch_pagespeed_insights(url: str) -> dict:
    if not PAGE_SPEED_API_KEY:
        raise RuntimeError("PAGE_SPEED_API_KEY not set")

    # percent‑encode the full URL
    encoded_url = quote(url, safe="")
    endpoint = (
        "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        f"?url={encoded_url}"
        "&category=performance"
        f"&key={PAGE_SPEED_API_KEY}"
    )

    print(f"[PSI] GET {endpoint}")     # ← now you will see this

    async with httpx.AsyncClient() as client:
        resp = await client.get(endpoint, timeout=30.0)
        resp.raise_for_status()
        return resp.json()
