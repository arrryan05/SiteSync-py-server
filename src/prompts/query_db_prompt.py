# src/prompts/query_db_prompt.py
import json
from typing import Any, Dict

def build_query_db_prompt(route: str, psi_data: Dict[str, Any]) -> str:
    """
    Build the natural‑language query string for Chroma.
    """
    metrics = psi_data["metrics"]
    diagnostics = psi_data.get("diagnostics", {})
    opportunities = psi_data.get("opportunities", [])

    opp_lines = "\n".join(
        f"- {o['id']} (weight: {o['score']})" for o in opportunities
    )

    return f"""
Find the code snippets most relevant to performance on route "{route}".
Performance metrics:
  • First Contentful Paint (FCP): {metrics["FCP"]}
  • Largest Contentful Paint (LCP): {metrics["LCP"]}
  • Cumulative Layout Shift (CLS): {metrics["CLS"]}
  • Total Blocking Time (TBT): {metrics["TBT"]}
Diagnostics:
  {json.dumps(diagnostics, indent=2)}
Opportunities:
{opp_lines}

Return the chunks of code that are likely responsible for these metrics
or could be tuned to improve them.
""".strip()
