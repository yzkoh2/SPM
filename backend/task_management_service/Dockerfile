FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 6001

CMD ["gunicorn", "--bind", "0.0.0.0:6001", "main:app"]

# Create uploads directory
RUN mkdir -p /app/uploads/tasks /app/uploads/subtasks

# Volume for persistent file storage
VOLUME ["/app/uploads"]
