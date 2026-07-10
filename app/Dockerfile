# =====================================================================
# STAGE 1: Compilation and Artifact Building Core Matrix
# =====================================================================
FROM python:3.13-slim AS builder

# Install temporary build headers required to compile Pillow wheels from source
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install dependencies into a separate local wheel directory path
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --target=/app/dependencies -r requirements.txt

# =====================================================================
# STAGE 2: Ultra-Slim Production Distroless Runtime Environment
# =====================================================================
FROM gcr.io/distroless/python3-debian12:latest

WORKDIR /app

# Pull down the compiled Python site-packages from the builder layer
COPY --from=builder /app/dependencies /app/dependencies

# Inject shared system graphics libraries natively bundled inside Debian 12
COPY --from=builder /usr/lib/x86_64-linux-gnu/libjpeg* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libz* /usr/lib/x86_64-linux-gnu/

# Copy your core application assets inside the working execution layout
COPY . .

# Point the Python interpreter layer to read the isolated dependencies directory
ENV PYTHONPATH=/app/dependencies
ENV PORT=8080

EXPOSE 8080

# Distroless has no shell (/bin/sh), so we call gunicorn directly via an explicit JSON array
ENTRYPOINT ["/app/dependencies/bin/gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--threads", "2", "app:app"]
