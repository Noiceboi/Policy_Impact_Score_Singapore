# Multi-stage Dockerfile for Policy Impact Assessment Framework
# Stage 1: Build stage
FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt requirements-lock.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements-lock.txt

# Stage 2: Production stage
FROM python:3.10-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/src"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create app directory structure
WORKDIR /app
RUN mkdir -p /app/{src,data,logs,output,tests} && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser src/ /app/src/
COPY --chown=appuser:appuser data/ /app/data/
COPY --chown=appuser:appuser templates/ /app/templates/
COPY --chown=appuser:appuser main.py /app/
COPY --chown=appuser:appuser LICENSE README.md /app/

# Install the package in development mode
RUN pip install -e .

# Switch to non-root user
USER appuser

# Expose port for dashboard
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8050/health || exit 1

# Default command
CMD ["python", "main.py"]

# Development stage
FROM production as development

# Switch back to root for development dependencies
USER root

# Install development dependencies
COPY requirements-dev.txt ./
RUN pip install -r requirements-dev.txt

# Install additional development tools
RUN apt-get update && apt-get install -y \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Copy test files
COPY --chown=appuser:appuser tests/ /app/tests/

# Switch back to app user
USER appuser

# Development command with auto-reload
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8050", "--debug"]
