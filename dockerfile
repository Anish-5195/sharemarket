# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (agar zarurat ho)
RUN apt-get update && apt-get install -y \
    netcat-traditional gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY require.txt .

# Install dependencies
RUN pip install --no-cache-dir -r require.txt

# Copy source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
