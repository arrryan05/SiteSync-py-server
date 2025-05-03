# # Use a slim Python base
# FROM python:3.10-slim

# # 1) Create & switch to /app
# WORKDIR /app

# ENV PYTHONPATH=/app/src

# # 2) Install build deps (git for cloning later, etc.)
# RUN apt-get update \
#   && apt-get install -y --no-install-recommends git build-essential \
#   && rm -rf /var/lib/apt/lists/*

# # 3) Copy & install Python deps
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt


# RUN python -m playwright install --with-deps


# # 4) Copy your source code
# COPY . .

# # 5) Expose FastAPI port
# EXPOSE 8080

# # 6) Default command: start Uvicorn
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]



# ┌────────────────────────────────────────────────────────────┐
# │ Dockerfile                                                 │
# └────────────────────────────────────────────────────────────┘

# 1) Base on the Playwright Python image (Ubuntu 24.04 “Noble” + Python + browsers)
FROM mcr.microsoft.com/playwright/python:v1.47.0

# 2) Set your working dir
WORKDIR /app

# 3) Ensure our app path is on PYTHONPATH
ENV PYTHONPATH=/app/src

# 4) Copy & install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copy all source
COPY . .

# 6) Expose port and launch
EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
