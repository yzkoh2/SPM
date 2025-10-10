FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 6001

# Set environment variable for unbuffered output
ENV PYTHONUNBUFFERED=1

# Use gunicorn with access log to stdout
CMD ["gunicorn", "--bind", "0.0.0.0:6001", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "debug", "main:app"]