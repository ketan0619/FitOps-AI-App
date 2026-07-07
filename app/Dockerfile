# Stage 1: Build dependencies using Python 3.11
FROM python:3.11-slim-bookworm AS builder
WORKDIR /app

# Install build tools and Pillow dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Target standard site-packages to ensure clean path resolution
RUN pip install --no-cache-dir --target=/install/site-packages -r requirements.txt

# Stage 2: Distroless Runtime matching Python 3.11 (Debian 12 Bookworm)
FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app

# 1. Copy the shared system libraries that Pillow needs to run
COPY --from=builder /usr/lib/x86_64-linux-gnu/libjpeg.so* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libz.so* /usr/lib/x86_64-linux-gnu/

# 2. Copy the Python packages into the correct Python 3.11 path
COPY --from=builder /install/site-packages /usr/lib/python3/dist-packages

# 3. Copy application files
COPY . .

EXPOSE 8080
ENV PORT=8080
ENV PYTHONPATH=/usr/lib/python3/dist-packages

ENTRYPOINT ["/usr/bin/python3", "-m", "gunicorn", "app:app", "-b", "0.0.0.0:8080", "--workers", "4", "--threads", "2"]

