# Multi-stage build for Parallax Voice Office
FROM python:3.10-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 processor && \
    mkdir -p /app/workspace /app/results /app/logs /app/task_configs /app/data /app/.backups /app/certs && \
    chown -R processor:processor /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/processor/.local

# Copy application files
COPY --chown=processor:processor *.py ./
COPY --chown=processor:processor *.yaml ./
COPY --chown=processor:processor *.yml ./
COPY --chown=processor:processor *.json ./
COPY --chown=processor:processor *.html ./
COPY --chown=processor:processor *.md ./
COPY --chown=processor:processor *.sh ./
COPY --chown=processor:processor task_configs/ ./task_configs/
COPY --chown=processor:processor .env.example ./

# Make shell scripts executable
USER root
RUN chmod +x *.sh 2>/dev/null || true
USER processor

# Create necessary directories with proper permissions
RUN mkdir -p workspace results logs data .backups .deleted certs && \
    chmod 755 workspace results logs data .backups .deleted && \
    chmod 700 certs

# Switch to non-root user
USER processor

# Add user's local bin to PATH
ENV PATH=/home/processor/.local/bin:$PATH

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PARALLAX_HOST=host.docker.internal
ENV PARALLAX_PORT=50051
ENV FLASK_ENV=production
ENV PYTHONDONTWRITEBYTECODE=1

# Expose ports (HTTP and HTTPS)
EXPOSE 5001
EXPOSE 5443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5001/api/status || exit 1

# Default command - use entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "obp-GUI.py"]