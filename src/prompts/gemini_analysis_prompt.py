# # src/prompts/gemini_analysis_prompt.py
# import json
# from typing import Any, Dict, List

# def create_gemini_prompt(
#     route: str,
#     trimmed_data: Dict[str, Any],
#     top_chunks: List[Dict[str, Any]]
# ) -> str:
#     # 1) Serialize the trimmed PSI data
#     psi_section = json.dumps(trimmed_data, indent=2)

#     # 2) Build the code‑snippets section
#     chunk_sections: List[str] = []
#     for idx, chunk in enumerate(top_chunks, start=1):
#         meta    = chunk["metadata"]
#         start   = meta.get("start_line", 1)
#         end     = meta.get("end_line", start)
#         path    = meta.get("relative_path", "<unknown>")
#         content = chunk.get("content", "")
#         lines   = content.splitlines()
#         snippet = "\n".join(
#             f"{start + i}: {line}" for i, line in enumerate(lines[:20])
#         )
#         truncated = "\n…(truncated)" if len(lines) > 20 else ""
#         chunk_sections.append(
#             f"--- Chunk {idx} ---\n"
#             f"File: {path} [lines {start}–{end}]\n"
#             f"{snippet}{truncated}"
#         )
#     chunks_section = "\n\n".join(chunk_sections) or "(no code snippets found)"

#     # 3) The “rules” text
#     rules = """
# Your task:
# For each metric (FCP, LCP, CLS, TBT) in the JSON skeleton below,
# populate its "recommendedSteps" array of strings according to these rules:

# 1. **Status** entry (always first):
#    - Must start with "Status: Good;", "Status: Moderate;", or "Status: Needs Improvement;"

# 2. **Code Change** entries (at least one per metric, **always**):
#    - Must start with "Code Change: from `<old code>` to `<new code>` in <file> lines X–Y; <explanation>"
#    - Reference one of the provided code snippets above.

# 3. **General Tips** entries (optional extras):
#    - Must start with "Tips: <concise recommendation>"

# 4. Do **NOT** modify the JSON structure or add extra fields.
# """.strip()

#     # 4) The JSON skeleton
#     json_template = (
#         "{\n"
#         f'  "route": "{route}",\n'
#         "  \"performanceData\": [\n"
#         "    {\n"
#         '      "FCP": {"value": "<string>", "recommendedSteps": []},\n'
#         '      "LCP": {"value": "<string>", "recommendedSteps": []},\n'
#         '      "CLS": {"value": "<string>", "recommendedSteps": []},\n'
#         '      "TBT": {"value": "<string>", "recommendedSteps": []}\n'
#         "    }\n"
#         "  ]\n"
#         "}"
#     )

#     # 5) Compose the full prompt
#     prompt = "\n".join([
#         "You are a senior performance-focused developer.",
#         f'Below is the PageSpeed Insights data for route "{route}"',
#         f"and the top {len(top_chunks)} relevant code snippets.",
#         "",
#         "=== PSI DATA ===",
#         psi_section,
#         "",
#         "=== CODE SNIPPETS ===",
#         chunks_section,
#         "",
#         rules,
#         "",
#         "Here is the JSON to update:",
#         json_template
#     ]).strip()

#     return prompt



# src/prompts/gemini_analysis_prompt.py
import json
from typing import Any, Dict, List

def create_gemini_prompt(
    route: str,
    trimmed_data: Dict[str, Any],
    top_chunks: List[Dict[str, Any]]
) -> str:
    # 1️⃣ PSI DATA section
    psi_section = json.dumps(trimmed_data, indent=2)

    # 2️⃣ CODE SNIPPETS section
    chunk_sections: List[str] = []
    for idx, chunk in enumerate(top_chunks, start=1):
        meta    = chunk["metadata"]
        start   = meta.get("start_line", 1)
        end     = meta.get("end_line", start)
        path    = meta.get("relative_path", "<unknown>")
        content = chunk.get("content", "")
        lines   = content.splitlines()
        snippet = "\n".join(
            f"{start + i}: {line}"
            for i, line in enumerate(lines[:20])
        )
        truncated = "\n…(truncated)" if len(lines) > 20 else ""
        chunk_sections.append(
            f"--- Chunk {idx} ---\n"
            f"File: {path} [lines {start}–{end}]\n"
            f"{snippet}{truncated}"
        )
    chunks_section = "\n\n".join(chunk_sections) or "(no code snippets found)"

    # 3️⃣ RULES + INLINE EXAMPLE for codeChanges
    rules_and_example = """
Your task:
For each metric (FCP, LCP, CLS, TBT) in the JSON skeleton below,
populate its "recommendedSteps" and "codeChanges" sections according to these rules:

1. **Status** entry (always first):
   - Must start with "Status: Good;", "Status: Moderate;", or "Status: Needs Improvement;"

2. **Code Change** entries (at least one per metric):
   - Go into the separate `codeChanges` field.
   - Each change must be an object with:
     - `file`: path to the file
     - `startLine`: integer
     - `endLine`: integer
     - `oldCode`: exact snippet before change
     - `newCode`: exact snippet after change
     - `explanation`: very brief rationale
   - Reference one of the provided code snippets above.

3. **General Tips** entries (optional extras):
   - Must start with "Tips: <concise recommendation>"

4. Do **NOT** modify the JSON structure or add extra fields.

# —— Example of a fully‐populated codeChanges entry for CLS ——  
# "codeChanges": {  
#   "CLS": [  
#     {  
#       "file": "src/components/Widget.jsx",  
#       "startLine": 10,  
#       "endLine": 12,  
#       "oldCode": "<div style=\\"width:auto\\">…</div>",  
#       "newCode": "<div style=\\"width:100px\\">…</div>",  
#       "explanation": "Reserve fixed width to prevent layout shift"  
#     }  
#   ],  
#   "FCP": [], "LCP": [], "TBT": []  
# }
""".strip()

    # 4️⃣ JSON skeleton with placeholders
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
        "  ],\n"
        "  \"codeChanges\": {\n"
        '    "FCP": <replace with an array of change‐objects>,\n'
        '    "LCP": <replace with an array of change‐objects>,\n'
        '    "CLS": <replace with an array of change‐objects>,\n'
        '    "TBT": <replace with an array of change‐objects>\n'
        "  }\n"
        "}"
    )

    # 5️⃣ Compose full prompt
    prompt = "\n\n".join([
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
        rules_and_example,
        "",
        "Here is the JSON to update:",
        json_template
    ])

    return prompt
