FROM python:3.11-slim-bookworm AS builder
WORKDIR /app

RUN apt-get update && apt-get upgrade && apt-get install -y --no-install-recommends \
    build-essential=* \
    libffi-dev=* \
    ssl-cert=* \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --target=/install/lib/python3/dist-packages -r requirements.txt

FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app
COPY --from=builder /install/lib/python3/dist-packages /usr/lib/python3/dist-packages
COPY . .

EXPOSE 8080
ENV PORT=8080
ENV OLLAMA_HOST=http://ollama-service.bankapp.svc.cluster.local:11434

ENTRYPOINT ["/usr/bin/python3", "-m", "gunicorn", "app:app", "-b", "0.0.0.0:8080", "--workers", "4", "--threads", "2"]

