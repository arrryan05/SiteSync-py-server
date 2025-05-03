# src/utils/extract_pagespeed_data.py
from typing import Any, Dict, List

def extract_relevant_pagespeed_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mirror your TS util: pull out url, overallScore, metrics, diagnostics, opportunities.
    """
    lr = data.get("lighthouseResult", {})
    audits = lr.get("audits", {})
    performance = lr.get("categories", {}).get("performance", {})
    details = audits.get("diagnostics", {}).get("details", {}).get("items", [{}])[0]

    return {
        "url": data.get("id"),
        "overallScore": performance.get("score"),
        "metrics": {
            "FCP": audits.get("first-contentful-paint", {}).get("displayValue"),
            "LCP": audits.get("largest-contentful-paint", {}).get("displayValue"),
            "CLS": audits.get("cumulative-layout-shift", {}).get("displayValue"),
            "TBT": audits.get("total-blocking-time", {}).get("displayValue"),
        },
        "diagnostics": details,
        "opportunities": [
            { "id": r.get("id"), "score": r.get("weight") }
            for r in performance.get("auditRefs", [])
            if r.get("group") == "load-opportunities"
        ],
    }
