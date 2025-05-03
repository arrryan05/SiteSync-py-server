# src/services/analysis_service.py
import json
from typing import List, Dict
from .pagespeed_service import fetch_pagespeed_insights
from .gemini_service import analyze_with_gemini
from .route_extractor import extract_all_routes    # your existing module
from utils.concurrency import run_with_concurrency
from utils.extract_pagespeed_data import extract_relevant_pagespeed_data
from prompts.gemini_analysis_prompt import create_gemini_prompt

async def analyze_website(url: str) -> List[Dict]:
    # 1️⃣ Extract routes
    routes = await extract_all_routes(url)

    # 2️⃣ Fetch PSI for each route (concurrency=2)
    page_data = await run_with_concurrency(
        routes,
        2,
        lambda r: fetch_pagespeed_insights(r)
    )

    # 3️⃣ Trim the data & call Gemini
    async def analyze_route(item):
        route, full = item
        if not full:
            return None
        trimmed = extract_relevant_pagespeed_data(full)
        prompt = create_gemini_prompt(route, trimmed)
        raw = await analyze_with_gemini(prompt)

        # strip out JSON substring
        first = raw.find("{")
        last = raw.rfind("}")
        body = raw[first:last+1] if first!=-1 and last!=-1 else raw
        try:
            obj = json.loads(body)
        except json.JSONDecodeError:
            obj = { "route": route, "error": raw }
        obj["route"] = route
        return obj

    paired = list(zip(routes, page_data))
    return await run_with_concurrency(paired, 2, analyze_route)
