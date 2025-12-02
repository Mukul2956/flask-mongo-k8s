# Use slim Python base
FROM python:3.11-slim

# Prevent python buffering in logs
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Create app directory
WORKDIR /app

# Install system dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy app
COPY app.py /app/

# Expose Flask port
EXPOSE 5000

# Healthcheck (simple)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -sf http://localhost:5000/ || exit 1

# Run
CMD ["python", "app.py"]