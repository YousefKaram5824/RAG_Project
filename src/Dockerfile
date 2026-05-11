FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    libgomp1 \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p assets/files assets/db/qdrant_data
EXPOSE 5000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
