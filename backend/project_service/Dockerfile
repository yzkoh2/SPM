FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 6002

CMD ["gunicorn", "--bind", "0.0.0.0:6002", "main:app"]

