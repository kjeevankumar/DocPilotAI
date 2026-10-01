FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Python dependencies first (layer caching)
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .

ENV PYTHONPATH=/app

# Expose port (Railway sets $PORT at runtime)
EXPOSE 8000

# Start the FastAPI app
CMD ["sh", "-c", "python3 -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
