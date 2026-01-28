# Dockerfile for Lattice Context Layer
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY pyproject.toml ./
COPY README.md ./
COPY LICENSE ./
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Create directory for user projects
RUN mkdir -p /workspace
WORKDIR /workspace

# Expose port for MCP server (if HTTP mode added in future)
EXPOSE 3000

# Default command shows help
CMD ["lattice", "--help"]
