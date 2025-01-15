FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_APP=wsgi.py \
    HOST=0.0.0.0 \
    PORT=5001

# Create necessary directories and set permissions
RUN mkdir -p uploads logs && \
    chmod 777 uploads logs

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5001

# Run the application with Gunicorn
CMD ["gunicorn", "--worker-class", "gthread", "--threads", "100", "-w", "1", "-b", "0.0.0.0:5001", "wsgi:app"] 