FROM python:3.13-slim

# Install system dependencies required to build Pillow C-extensions cleanly
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first to utilize Docker layer caching
COPY requirements.txt .

# Force a clean, binary-independent source installation of Pillow and reportlab
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --force-reinstall pillow reportlab && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--threads", "2", "app:app"]
