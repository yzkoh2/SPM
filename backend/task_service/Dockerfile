FROM python:3.13-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgobject-2.0-0 \
    libfontconfig1 \
    libffi-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 6001

# Set environment variable for unbuffered output
ENV PYTHONUNBUFFERED=1

# Use gunicorn with access log to stdout
CMD ["gunicorn", "--bind", "0.0.0.0:6001", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "debug", "main:app"]