# =============================================================================
# Dockerfile — FastAPI Application Container
# =============================================================================
# PURPOSE:
#   Builds a container image for the FastAPI RAG backend.
#   The TA must be able to run the entire system with: docker-compose up
#
# BUILD STRATEGY:
#   Two-stage dependency installation for fast rebuilds:
#     1. Copy requirements.txt FIRST (Docker caches this layer)
#     2. pip install (only reruns when requirements.txt changes)
#     3. Copy source code LAST (changes here don't invalidate pip cache)
#
# TEAM NOTE (Pair B — Member 5):
#   Test this locally before the final submission:
#     cd rag-project
#     docker build -t rag-app ./src
#     docker run -p 5000:5000 --env-file src/.env rag-app
#   Then verify http://localhost:5000/docs is accessible.
# =============================================================================

FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies needed by some Python packages
# (PyMuPDF needs libgomp1, sentence-transformers may need gcc)
RUN apt-get update && apt-get install -y \
    libgomp1 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ── Layer 1: Install Python dependencies (cached unless requirements.txt changes) ──
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Layer 2: Copy application source code ──────────────────────────────────
COPY . .

# Create runtime directories that would normally be gitignored
RUN mkdir -p assets/files assets/db/qdrant_data

# Expose the FastAPI port
EXPOSE 5000

# Start the server
# --host 0.0.0.0 makes it accessible from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
