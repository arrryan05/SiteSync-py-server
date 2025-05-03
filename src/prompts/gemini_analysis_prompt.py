# src/prompts/gemini_analysis_prompt.py
from typing import Any, Dict

def create_gemini_prompt(route: str, trimmed: Dict[str, Any]) -> str:
    psi = trimmed
    return f"""
You are an expert website performance engineer.  
Analyze the following PageSpeed Insights data for the route "{route}":

{psi}

**IMPORTANT**:  
Return ONLY a JSON object, no markdown fences or extra text, matching this schema:

{{
  "route": "{route}",
  "performanceData": [
    {{
      "FCP": {{ "value": string, "recommendedSteps": string[] }},
      "LCP": {{ "value": string, "recommendedSteps": string[] }},
      "CLS": {{ "value": string, "recommendedSteps": string[] }},
      "TBT": {{ "value": string, "recommendedSteps": string[] }}
    }}
  ]
}}
"""
