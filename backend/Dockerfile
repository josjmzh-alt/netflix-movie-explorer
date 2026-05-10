FROM python:3.11-slim

WORKDIR /app

# Install dependencies first — separate layer so it's cached on rebuilds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source package
COPY app ./app

# credentials/ is mounted as a volume at runtime — not baked into the image
# This keeps secrets out of the image and lets token.json persist across restarts
RUN mkdir -p credentials

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
