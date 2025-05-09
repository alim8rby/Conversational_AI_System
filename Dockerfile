# 1. Base image
FROM python:3.11-slim

# 2. System deps for gTTS and Together AI
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libssl-dev libglib2.0-0 libnss3 libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3. Set working directory
WORKDIR /app

# 4. Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy code
COPY . .

# 6. Expose port and start server
EXPOSE 8000
CMD ["python", "app.py"]
