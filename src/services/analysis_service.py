# src/services/analysis_service.py
import json
import re
from typing import List, Dict
from .pagespeed_service import fetch_pagespeed_insights
from .gemini_service import analyze_with_gemini
from .route_extractor import extract_all_routes    # your existing module
from utils.concurrency import run_with_concurrency
from utils.extract_pagespeed_data import extract_relevant_pagespeed_data
from prompts.gemini_analysis_prompt import create_gemini_prompt

async def analyze_website(url: str) -> List[Dict]:
    # 1️⃣ Extract routes
    print("[ANALYSIS] 1. extracting routes…")
    routes = await extract_all_routes(url)
    print(f"[ANALYSIS]  → got routes: {routes!r}")

    # 2️⃣ Fetch PSI for each route (concurrency=2)
    print("[ANALYSIS] 2. fetching PageSpeed insights…")
    page_data = await run_with_concurrency(
        routes,
        2,
        lambda r: fetch_pagespeed_insights(r)
    )
    
    for i, (route, data) in enumerate(zip(routes, page_data)):
        print(f"[ANALYSIS]   route #{i} {route!r} → PSI data is {'present' if data else 'MISSING'}")

    # 3️⃣ Trim the data & call Gemini
    async def analyze_route(item):
        route, full = item
        print(f"[ANALYSIS] 3. analyzing route {route!r}…")

        if not full:
            print(f"[ANALYSIS]   ⚠️ skipping {route!r} (no PSI data)")
            return None
        trimmed = extract_relevant_pagespeed_data(full)
        print(f"[ANALYSIS]   trimmed data for {route!r}: {trimmed!r}")
        prompt = create_gemini_prompt(route, trimmed)
        raw = await analyze_with_gemini(prompt)
        print(f"[ANALYSIS]   raw Gemini response for {route!r}: {raw!r}")

        # strip out JSON substring
        first = raw.find("{")
        last = raw.rfind("}")
        body = raw[first:last+1] if first!=-1 and last!=-1 else raw
        try:
            obj = json.loads(body)
        except json.JSONDecodeError:
            obj = { "route": route, "error": raw }
        obj["route"] = route
        
        # —––––––– sanitize all metric values –––––––—
        for entry in obj.get("performanceData", []):
            for metric in ("FCP","LCP","CLS","TBT"):
                val = entry[metric]["value"]
                clean = re.sub(r"\s+", " ", val).strip()
                entry[metric]["value"] = clean
                
        return obj

    paired = list(zip(routes, page_data))
    results = await run_with_concurrency(paired, 2, analyze_route)
    print(f"[ANALYSIS] finished all routes, got: {results!r}")
    return results
