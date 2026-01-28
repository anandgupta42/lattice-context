# Docker Usage Guide

## Quick Start

### Pull Pre-built Image

```bash
docker pull altimateai/lattice-context:latest
```

### Or Build Locally

```bash
git clone https://github.com/altimate-ai/lattice-context.git
cd lattice-context
docker build -t lattice-context:local .
```

## Basic Usage

### Initialize in dbt Project

```bash
cd /path/to/your/dbt/project
docker run -it --rm \
  -v $(pwd):/workspace \
  altimateai/lattice-context:latest \
  lattice init
```

### Index Project

```bash
docker run -it --rm \
  -v $(pwd):/workspace \
  altimateai/lattice-context:latest \
  lattice index
```

### Query Context

```bash
docker run -it --rm \
  -v $(pwd):/workspace \
  altimateai/lattice-context:latest \
  lattice context "add revenue to orders"
```

### Start MCP Server

```bash
# Run in background
docker run -d \
  --name lattice-server \
  -v $(pwd):/workspace \
  altimateai/lattice-context:latest \
  lattice serve

# View logs
docker logs -f lattice-server

# Stop server
docker stop lattice-server
```

## Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  lattice:
    image: altimateai/lattice-context:latest
    container_name: lattice-context
    volumes:
      - ./:/workspace
    working_dir: /workspace
    command: lattice serve
    stdin_open: true
    tty: true
    environment:
      - LATTICE_LOG_LEVEL=INFO
    restart: unless-stopped
```

Then:

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LATTICE_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `LATTICE_DB_PATH` | Custom database path | `.lattice/index.db` |
| `LATTICE_CONFIG_PATH` | Custom config path | `.lattice/config.yml` |

Example:

```bash
docker run -it --rm \
  -v $(pwd):/workspace \
  -e LATTICE_LOG_LEVEL=DEBUG \
  altimateai/lattice-context:latest \
  lattice index --verbose
```

## Volume Mounts

The Docker container needs access to:

1. **Your dbt project** (read-only for indexing, read-write for .lattice/)
2. **Git history** (read-only, for decision extraction)

### Minimal Setup

```bash
# Mount just the dbt project
docker run -v $(pwd):/workspace ...
```

### Custom Paths

```bash
# If dbt project is in a subdirectory
docker run -v $(pwd)/dbt_project:/workspace ...

# Multiple mount points
docker run \
  -v $(pwd):/project \
  -v $(pwd)/.lattice:/data \
  -e LATTICE_DB_PATH=/data/index.db \
  altimateai/lattice-context:latest
```

## Claude Desktop Integration

### Option 1: Connect to Running Container

In `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "lattice": {
      "command": "docker",
      "args": [
        "exec",
        "lattice-server",
        "lattice",
        "serve"
      ]
    }
  }
}
```

### Option 2: Use Installed Package

Docker is better for testing. For production use with Claude Desktop, install with pip:

```bash
pip install lattice-context
```

Then:

```json
{
  "mcpServers": {
    "lattice": {
      "command": "lattice",
      "args": ["serve"]
    }
  }
}
```

## Troubleshooting

### Permission Issues

If you get permission errors:

```bash
# Fix ownership of .lattice directory
docker run -it --rm \
  -v $(pwd):/workspace \
  altimateai/lattice-context:latest \
  chown -R $(id -u):$(id -g) /workspace/.lattice
```

### Container Can't Find manifest.json

Make sure you've compiled your dbt project:

```bash
# On host
cd your-dbt-project
dbt compile

# Then index with Docker
docker run -it --rm \
  -v $(pwd):/workspace \
  altimateai/lattice-context:latest \
  lattice index
```

### Git History Not Found

The container needs access to .git directory:

```bash
# Make sure .git is in the mounted directory
ls -la .git  # Should exist

# Check git works in container
docker run -it --rm \
  -v $(pwd):/workspace \
  altimateai/lattice-context:latest \
  git log --oneline -5
```

## Building Custom Images

### With Additional Tools

```dockerfile
FROM altimateai/lattice-context:latest

# Install additional tools
RUN pip install dbt-core dbt-snowflake

# Custom entrypoint
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

### Multi-stage Build

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --user .

# Runtime stage
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
CMD ["lattice", "--help"]
```

## Performance Tips

### Use BuildKit

```bash
DOCKER_BUILDKIT=1 docker build -t lattice-context:latest .
```

### Cache Dependencies

The Dockerfile is optimized to cache pip dependencies. Only rebuild when dependencies change.

### Faster Indexing

```bash
# Limit git history for faster first index
docker run -it --rm \
  -v $(pwd):/workspace \
  altimateai/lattice-context:latest \
  lattice index --limit 100
```

## Production Deployment

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lattice-context
spec:
  replicas: 1
  selector:
    matchLabels:
      app: lattice
  template:
    metadata:
      labels:
        app: lattice
    spec:
      containers:
      - name: lattice
        image: altimateai/lattice-context:latest
        command: ["lattice", "serve"]
        volumeMounts:
        - name: dbt-project
          mountPath: /workspace
          readOnly: true
        - name: lattice-data
          mountPath: /workspace/.lattice
      volumes:
      - name: dbt-project
        persistentVolumeClaim:
          claimName: dbt-project-pvc
      - name: lattice-data
        persistentVolumeClaim:
          claimName: lattice-data-pvc
```

### Docker Swarm

```yaml
version: '3.8'

services:
  lattice:
    image: altimateai/lattice-context:latest
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
    volumes:
      - dbt-project:/workspace:ro
      - lattice-data:/workspace/.lattice
    command: lattice serve

volumes:
  dbt-project:
    driver: local
  lattice-data:
    driver: local
```

## Support

Issues with Docker? Please report at:
https://github.com/altimate-ai/lattice-context/issues

Include:
- Docker version (`docker --version`)
- Image tag you're using
- Full error message
- Output of `docker logs <container-id>`
