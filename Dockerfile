FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install WeasyPrint native dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libglib2.0-0 \
    libffi8 \
    shared-mime-info \
    fonts-dejavu \
    fonts-liberation \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps in a venv
COPY requirements.txt ./
RUN python -m venv /opt/venv \
 && . /opt/venv/bin/activate \
 && pip install --no-cache-dir -r requirements.txt
ENV PATH="/opt/venv/bin:${PATH}"

# Copy source
COPY . .

# Default start command (Railway may override with startCommand)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]


