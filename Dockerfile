# AutoCrate Development Environment
# Multi-stage Docker build for development and production

# Development stage
FROM python:3.11-slim as development

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    git \
    tk-dev \
    python3-tk \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for development
RUN useradd -m -u 1000 developer && \
    chown -R developer:developer /app
USER developer

# Copy requirements first for better caching
COPY --chown=developer:developer requirements*.txt ./

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt && \
    pip install --user --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY --chown=developer:developer . .

# Set environment variables
ENV PYTHONPATH=/app
ENV DISPLAY=:99
ENV PATH=/home/developer/.local/bin:$PATH

# Expose port for development server (if needed)
EXPOSE 8000

# Default command for development
CMD ["python", "nx_expressions_generator.py"]

# Production stage
FROM python:3.11-slim as production

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1001 autocrate && \
    chown -R autocrate:autocrate /app
USER autocrate

# Copy requirements
COPY --chown=autocrate:autocrate requirements.txt ./

# Install production dependencies only
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=autocrate:autocrate *.py ./
COPY --chown=autocrate:autocrate docs/ ./docs/
COPY --chown=autocrate:autocrate LICENSE ./
COPY --chown=autocrate:autocrate README.md ./

# Set environment
ENV PYTHONPATH=/app
ENV PATH=/home/autocrate/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import nx_expressions_generator; print('AutoCrate healthy')"

# Run as non-root
CMD ["python", "nx_expressions_generator.py"]

# Testing stage
FROM development as testing

# Copy test files
COPY --chown=developer:developer tests/ ./tests/

# Install additional test dependencies
RUN pip install --user pytest-cov pytest-benchmark pytest-xvfb

# Set up virtual display for GUI testing
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &\nexec "$@"' > /usr/local/bin/xvfb-run-safe && \
    chmod +x /usr/local/bin/xvfb-run-safe

# Run tests by default
CMD ["xvfb-run-safe", "python", "-m", "pytest", "tests/", "-v", "--cov=."]