# Multi-stage build for Python Edge Functions
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy dependency files
COPY pyproject.toml ./

# Fix hatchling packaging on-the-fly for local development
RUN if [ -f pyproject.toml ] && ! grep -q "tool.hatch.build.targets.wheel" pyproject.toml; then \
    printf "\n[tool.hatch.build.targets.wheel]\npackages = [\"function\"]\n" >> pyproject.toml; \
fi

# Install dependencies to a temporary location
RUN pip install --user --no-cache-dir . uvicorn

# Stage 2: Runtime image
FROM python:3.11-slim

WORKDIR /app

# Add Python dependencies from builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:$PATH"

# Copy application files
COPY function/ ./function/
COPY func.toml .
COPY app.py .

# Expose HTTP port
EXPOSE 8080

# Healthcheck for local testing and orchestration
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run with safe defaults for edge compute
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "5"]