# src/services/gemini_service.py
import os
from google import genai
from google.genai.types import Schema, Type

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

# Initialize the client (Developer API mode by default)
client = genai.Client(api_key=GEMINI_API_KEY)  # :contentReference[oaicite:1]{index=1}

async def analyze_with_gemini(prompt: str) -> str:
    # Define the JSON schema you want back
    response_schema: Schema = {
        "type": Type.OBJECT,
        "properties": {
            "route": {"type": Type.STRING},
            "performanceData": {
                "type": Type.ARRAY,
                "minItems": 1,
                "maxItems": 1,
                "items": {
                    "type": Type.OBJECT,
                    "properties": {
                        metric: {
                            "type": Type.OBJECT,
                            "properties": {
                                "value": {"type": Type.STRING},
                                "recommendedSteps": {
                                    "type": Type.ARRAY,
                                    "items": {"type": Type.STRING},
                                },
                            },
                            "required": ["value", "recommendedSteps"],
                        }
                        for metric in ("FCP", "LCP", "CLS", "TBT")
                    },
                    "required": ["FCP", "LCP", "CLS", "TBT"],
                },
            },
        },
        "required": ["route", "performanceData"],
    }

    # Call the API
    resp = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config={
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        },
    )
    return resp.text or ""
