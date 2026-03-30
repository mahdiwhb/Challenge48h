FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY app/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY data/ /app/data/
COPY app/backend/ /app/app/backend/

# Create data directory for SQLite
RUN mkdir -p /app/app/backend/data

EXPOSE 8000

CMD ["uvicorn", "app.backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
