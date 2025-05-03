# src/services/gemini_service.py
import os
import google.generativeai as genai
from google.generativeai.types import Schema, Type  # adjust import path if needed

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.0-flash"

# Configure the SDK once at module load
genai.configure(api_key=GEMINI_API_KEY)

async def analyze_with_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set")

    # Build your response schema exactly as before
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

    # Instantiate the model and call it
    model = genai.GenerativeModel(MODEL_NAME)
    resp = await model.generate_content(
        prompt=prompt,
        config={
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        },
    )
    return resp.text or ""
