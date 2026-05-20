FROM python:3.10-slim

WORKDIR /app

# Copy requirements from the root folder
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from your local /app folder into the container's /app folder
COPY app/ .

CMD ["python", "app.py"]

