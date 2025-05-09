# ┌────────────────────────────────────────────────────────────┐
# │ Dockerfile                                                 │
# └────────────────────────────────────────────────────────────┘

# 1) Base image: Playwright Python (Ubuntu 24.04 “Noble” + Python + browsers)
FROM mcr.microsoft.com/playwright/python:v1.52.0-noble

# 2) Set working directory
WORKDIR /app

# 3) Ensure our app path is on PYTHONPATH
ENV PYTHONPATH=/app/src

# 4) Copy & install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) PRE‑DOWNLOAD the all‑MiniLM‑L6‑v2 ONNX model into the build cache
#    (removes network timeout issues at runtime)
RUN python - <<EOF
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
# This will download the model into /root/.cache/chroma/onnx_models
ONNXMiniLM_L6_V2()._download_model_if_not_exists()
print("✅ ONNX MiniLM L6 V2 model pre‑downloaded.")
EOF

# 6) Copy application source
COPY . .

# 7) Expose port and launch
EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
