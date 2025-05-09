# # src/prompts/gemini_analysis_prompt.py
# from typing import Any, Dict

# def create_gemini_prompt(route: str, trimmed: Dict[str, Any]) -> str:
#     psi = trimmed
#     return f"""
# You are an expert website performance engineer.  
# Analyze the following PageSpeed Insights data for the route "{route}":

# {psi}

# **IMPORTANT**:  
# Return ONLY a JSON object, no markdown fences or extra text, matching this schema:

# {{
#   "route": "{route}",
#   "performanceData": [
#     {{
#       "FCP": {{ "value": string, "recommendedSteps": string[] }},
#       "LCP": {{ "value": string, "recommendedSteps": string[] }},
#       "CLS": {{ "value": string, "recommendedSteps": string[] }},
#       "TBT": {{ "value": string, "recommendedSteps": string[] }}
#     }}
#   ]
# }}
# """
# src/prompts/gemini_analysis_prompt.py
import json
from typing import Any, Dict, List

def create_gemini_prompt(
    route: str,
    trimmed_data: Dict[str, Any],
    top_chunks: List[Dict[str, Any]]
) -> str:
    # 1) Serialize the trimmed PSI data
    psi_section = json.dumps(trimmed_data, indent=2)

    # 2) Build the code‑snippets section
    chunk_sections: List[str] = []
    for idx, chunk in enumerate(top_chunks, start=1):
        meta    = chunk["metadata"]
        start   = meta.get("start_line", 1)
        end     = meta.get("end_line", start)
        path    = meta.get("relative_path", "<unknown>")
        content = chunk.get("content", "")
        lines   = content.splitlines()
        snippet = "\n".join(
            f"{start + i}: {line}" for i, line in enumerate(lines[:20])
        )
        truncated = "\n…(truncated)" if len(lines) > 20 else ""
        chunk_sections.append(
            f"--- Chunk {idx} ---\n"
            f"File: {path} [lines {start}–{end}]\n"
            f"{snippet}{truncated}"
        )
    chunks_section = "\n\n".join(chunk_sections) or "(no code snippets found)"

    # 3) The “rules” text
    rules = """
Your task:
For each metric (FCP, LCP, CLS, TBT) in the JSON skeleton below,
populate its "recommendedSteps" array of strings according to these rules:

1. **Status** entry (always first):
   - Must start with "Status: Good;", "Status: Moderate;", or "Status: Needs Improvement;"

2. **Code Change** entries (at least one per metric, **always**):
   - Must start with "Code Change: from `<old code>` to `<new code>` in <file> lines X–Y; <explanation>"
   - Reference one of the provided code snippets above.

3. **General Tips** entries (optional extras):
   - Must start with "Tips: <concise recommendation>"

4. Do **NOT** modify the JSON structure or add extra fields.
""".strip()

    # 4) The JSON skeleton
    json_template = (
        "{\n"
        f'  "route": "{route}",\n'
        "  \"performanceData\": [\n"
        "    {\n"
        '      "FCP": {"value": "<string>", "recommendedSteps": []},\n'
        '      "LCP": {"value": "<string>", "recommendedSteps": []},\n'
        '      "CLS": {"value": "<string>", "recommendedSteps": []},\n'
        '      "TBT": {"value": "<string>", "recommendedSteps": []}\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    # 5) Compose the full prompt
    prompt = "\n".join([
        "You are a senior performance-focused developer.",
        f'Below is the PageSpeed Insights data for route "{route}"',
        f"and the top {len(top_chunks)} relevant code snippets.",
        "",
        "=== PSI DATA ===",
        psi_section,
        "",
        "=== CODE SNIPPETS ===",
        chunks_section,
        "",
        rules,
        "",
        "Here is the JSON to update:",
        json_template
    ]).strip()

    return prompt
