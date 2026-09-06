FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and data
COPY app/ ./app/
COPY data/ ./data/

EXPOSE 8000

ENV VECTOR_STORE_PATH="/app/data/vector_store"
ENV OLLAMA_BASE_URL="http://host.docker.internal:11434"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
