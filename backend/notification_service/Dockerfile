FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 6003

# Set environment variable for unbuffered output
ENV PYTHONUNBUFFERED=1

# Use Python directly for better logging
CMD ["python", "-u", "main.py"]