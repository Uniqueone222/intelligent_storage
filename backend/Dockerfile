FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    python3-dev \
    libmagic1 \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (use minimal requirements)
COPY requirements_minimal.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements_minimal.txt --no-cache-dir

# Copy project files
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/media /app/static /app/logs

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Run server (overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
