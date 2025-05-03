# Use a slim Python base
FROM python:3.10-slim

# 1) Create & switch to /app
WORKDIR /app

ENV PYTHONPATH=/app/src

# 2) Install build deps (git for cloning later, etc.)
RUN apt-get update \
  && apt-get install -y --no-install-recommends git build-essential \
  && rm -rf /var/lib/apt/lists/*

# 3) Copy & install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copy your source code
COPY . .

# 5) Expose FastAPI port
EXPOSE 8080

# 6) Default command: start Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
