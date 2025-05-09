# # src/services/analysis_service.py
# import json
# import re
# from typing import List, Dict
# from .pagespeed_service import fetch_pagespeed_insights
# from .gemini_service import analyze_with_gemini
# from .route_extractor import extract_all_routes    # your existing module
# from utils.concurrency import run_with_concurrency
# from utils.extract_pagespeed_data import extract_relevant_pagespeed_data
# from prompts.gemini_analysis_prompt import create_gemini_prompt
# from services.code_analyzer.orchechtrator import orchestrator
# from services.code_analyzer.vector_search import query_top_chunks

# async def analyze_website(url: str, name:str, gitUrl:str=None) -> List[Dict]:
    
#     if gitUrl:
#         orchestrator(gitUrl, name)
#         print(f"[ANALYSIS] cloned & stored code from {gitUrl} into '{name}' collection")
        
#     # 1️⃣ Extract routes
#     print("[ANALYSIS] 1. extracting routes…")
#     routes = await extract_all_routes(url)
#     print(f"[ANALYSIS]  → got routes: {routes!r}")

#     # 2️⃣ Fetch PSI for each route (concurrency=2)
#     print("[ANALYSIS] 2. fetching PageSpeed insights…")
#     page_data = await run_with_concurrency(
#         routes,
#         2,
#         lambda r: fetch_pagespeed_insights(r)
#     )
    
#     for i, (route, data) in enumerate(zip(routes, page_data)):
#         print(f"[ANALYSIS]   route #{i} {route!r} → PSI data is {'present' if data else 'MISSING'}")

#     # 3️⃣ Trim the data & call Gemini
#     async def analyze_route(item):
#         route, full = item
#         print(f"[ANALYSIS] 3. analyzing route {route!r}…")

#         if not full:
#             print(f"[ANALYSIS]   ⚠️ skipping {route!r} (no PSI data)")
#             return None
#         trimmed = extract_relevant_pagespeed_data(full)
#         print(f"[ANALYSIS]   trimmed data for {route!r}: {trimmed!r}")
        
#         top_chunks = []
#         if gitUrl:
#             top_chunks = query_top_chunks(
#                 route,
#                 trimmed,
#                 collection_name=name,
#                 top_k=5
#             )
#             print(f"[ANALYSIS]   retrieved {len(top_chunks)} code chunks")
            
            
#         prompt = create_gemini_prompt(route, trimmed, top_chunks)
#         raw = await analyze_with_gemini(prompt)
#         print(f"[ANALYSIS]   raw Gemini response for {route!r}: {raw!r}")

#         # strip out JSON substring
#         first = raw.find("{")
#         last = raw.rfind("}")
#         body = raw[first:last+1] if first!=-1 and last!=-1 else raw
#         try:
#             obj = json.loads(body)
#         except json.JSONDecodeError:
#             obj = { "route": route, "error": raw }
#         obj["route"] = route
        
#         # —––––––– sanitize all metric values –––––––—
#         for entry in obj.get("performanceData", []):
#             for metric in ("FCP","LCP","CLS","TBT"):
#                 val = entry[metric]["value"]
#                 clean = re.sub(r"\s+", " ", val).strip()
#                 entry[metric]["value"] = clean
                
#         return obj

#     paired = list(zip(routes, page_data))
#     results = await run_with_concurrency(paired, 2, analyze_route)
#     filtered: List[Dict] = [r for r in results if isinstance(r, dict)]
#     print(f"[ANALYSIS] finished all routes, got: {filtered!r}")
#     return filtered



# src/services/analysis_service.py

import json
import re
import traceback
from typing import List, Dict

from .pagespeed_service import fetch_pagespeed_insights
from .gemini_service import analyze_with_gemini
from .route_extractor import extract_all_routes
from utils.concurrency import run_with_concurrency
from utils.extract_pagespeed_data import extract_relevant_pagespeed_data
from prompts.gemini_analysis_prompt import create_gemini_prompt
from services.code_analyzer.orchechtrator import orchestrator
from services.code_analyzer.vector_search import query_top_chunks


async def analyze_website(
    url: str,
    name: str,
    gitUrl: str = None
) -> List[Dict]:
    # 0️⃣ If a Git repo was provided, clone/chunk/store into Chroma
    if gitUrl:
        orchestrator(gitUrl, name)
        print(f"[ANALYSIS] cloned & stored code from {gitUrl} into '{name}' collection")

    # 1️⃣ Extract all routes
    print("[ANALYSIS] 1. extracting routes…")
    routes = await extract_all_routes(url)
    print(f"[ANALYSIS]  → got routes: {routes!r}")

    # 2️⃣ Fetch PageSpeed Insights for each route (concurrency=2)
    print("[ANALYSIS] 2. fetching PageSpeed insights…")
    page_data = await run_with_concurrency(
        routes,
        2,
        lambda r: fetch_pagespeed_insights(r)
    )
    for i, (route, data) in enumerate(zip(routes, page_data)):
        status = "present" if data else "MISSING"
        print(f"[ANALYSIS]   route #{i} {route!r} → PSI data is {status}")

    # 3️⃣ Analyze each route
    async def analyze_route(item):
        route, full = item
        print(f"[ANALYSIS] 3. analyzing route {route!r}…")

        if not full:
            print(f"[ANALYSIS]   ⚠️ skipping {route!r} (no PSI data)")
            return {
                "route": route,
                "performanceData": [
                    {
                        "FCP": {"value": "N/A", "recommendedSteps": ["No PSI data"]},
                        "LCP": {"value": "N/A", "recommendedSteps": ["No PSI data"]},
                        "CLS": {"value": "N/A", "recommendedSteps": ["No PSI data"]},
                        "TBT": {"value": "N/A", "recommendedSteps": ["No PSI data"]},
                    }
                ],
            }

        try:
            # Trim raw PSI response
            trimmed = extract_relevant_pagespeed_data(full)
            print(f"[ANALYSIS]   trimmed data for {route!r}: {trimmed!r}")

            # Retrieve top code chunks if we have a repo
            top_chunks = []
            if gitUrl:
                top_chunks = query_top_chunks(
                    route,
                    trimmed,
                    collection_name=name,
                    top_k=5
                )
                print(f"[ANALYSIS]   retrieved {len(top_chunks)} code chunks")

            # Build and send prompt to Gemini
            prompt = create_gemini_prompt(route, trimmed, top_chunks)
            print("––––––––––––––––––––––––––––––––––––––––––––––––––––––––––")
            print("Gemini Prompt:\n", prompt)
            print("––––––––––––––––––––––––––––––––––––––––––––––––––––––––––")
            raw = await analyze_with_gemini(prompt)
            print(f"[ANALYSIS]   raw Gemini response for {route!r}: {raw!r}")

            # Extract JSON substring
            first = raw.find("{")
            last = raw.rfind("}")
            body = raw[first:last+1] if first != -1 and last != -1 else raw

            try:
                obj = json.loads(body)
            except json.JSONDecodeError:
                obj = {"route": route, "error": raw}

            obj["route"] = route

            # Sanitize metric values
            for entry in obj.get("performanceData", []):
                for metric in ("FCP", "LCP", "CLS", "TBT"):
                    val = entry[metric]["value"]
                    clean = re.sub(r"\s+", " ", val).strip()
                    entry[metric]["value"] = clean

            return obj

        except Exception as e:
            print(f"[ANALYSIS] ❌ error analyzing {route!r}: {e!r}")
            traceback.print_exc()
            # Return a minimal valid result rather than None
            return {
                "route": route,
                "performanceData": [
                    {
                        "FCP": {"value": "N/A", "recommendedSteps": ["Internal error"]},
                        "LCP": {"value": "N/A", "recommendedSteps": ["Internal error"]},
                        "CLS": {"value": "N/A", "recommendedSteps": ["Internal error"]},
                        "TBT": {"value": "N/A", "recommendedSteps": ["Internal error"]},
                    }
                ],
            }

    paired = list(zip(routes, page_data))
    results = await run_with_concurrency(paired, 2, analyze_route)

    # 4️⃣ Log and return every result, including error skeletons
    print(f"[ANALYSIS] finished all routes, got: {results!r}")
    return results
