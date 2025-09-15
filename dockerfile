# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies 
RUN apt-get update && apt-get install -y \
    netcat-traditional gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY require.txt .

RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    python3-dev \
    libdbus-1-dev \
    libcups2-dev \
    libdbus-1-dev \
    libglib2.0-dev \
    libcairo2-dev \
    libgirepository1.0-dev \
    gir1.2-gtk-3.0 \
    cmake \
    build-essential \
    python3-dev \
    pkg-config


# Install dependencies
RUN pip install --no-cache-dir -r require.txt

# Copy source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
