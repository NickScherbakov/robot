# Docker Deployment Guide

This guide explains how to deploy the Earning Robot using Docker.

## Prerequisites

- Docker installed
- Docker Compose installed
- `.env` file configured

## Quick Start with Docker

### 1. Build the Image

```bash
docker build -t earning-robot .
```

### 2. Run with Docker Compose

```bash
# Make sure .env is configured
cp .env.example .env
# Edit .env with your credentials

# Start the robot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the robot
docker-compose down
```

### 3. Run with Docker Only

```bash
docker run -d \
  --name earning-robot \
  --env-file .env \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  earning-robot
```

## Viewing Logs

```bash
# Docker Compose
docker-compose logs -f

# Docker
docker logs -f earning-robot
```

## Updating

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## Health Check

```bash
# Check if container is healthy
docker ps

# Manual health check
curl http://localhost:5000/health
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker-compose logs
```

### Database issues

Remove and recreate:
```bash
docker-compose down
rm -rf data/
docker-compose up -d
```

### Port conflicts

Change port in `.env`:
```env
PORT=5001
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

## Production Deployment

### Using Docker Swarm

```bash
docker swarm init
docker stack deploy -c docker-compose.yml robot
```

### Using Kubernetes

See `k8s/` directory for Kubernetes manifests (if available).

### Environment Variables in Production

Never commit `.env` to version control. Use:

- Docker secrets
- Kubernetes secrets
- Cloud provider secret management
- Environment variable injection

Example with Docker secrets:

```bash
echo "your_token" | docker secret create telegram_token -
```

Update `docker-compose.yml`:
```yaml
services:
  robot:
    secrets:
      - telegram_token
    environment:
      - TELEGRAM_BOT_TOKEN_FILE=/run/secrets/telegram_token

secrets:
  telegram_token:
    external: true
```

## Multi-Stage Build (Advanced)

For smaller images, use multi-stage builds:

```dockerfile
# Build stage
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "main.py"]
```

## Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  robot:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## Backup and Restore

### Backup

```bash
# Backup database and data
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Or use Docker volume backup
docker run --rm \
  -v earning-robot_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/data-backup.tar.gz /data
```

### Restore

```bash
# Extract backup
tar -xzf backup-20250115.tar.gz

# Restart container
docker-compose restart
```

## Monitoring

Use Docker stats:
```bash
docker stats earning-robot
```

Or integrate with monitoring tools:
- Prometheus
- Grafana
- Datadog
- New Relic

## Security

1. **Don't run as root:**
   Add to Dockerfile:
   ```dockerfile
   RUN useradd -m appuser
   USER appuser
   ```

2. **Use secrets for sensitive data**

3. **Keep images updated:**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

4. **Scan for vulnerabilities:**
   ```bash
   docker scan earning-robot
   ```

## Cloud Deployment

### AWS ECS

```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <ecr-url>
docker tag earning-robot:latest <ecr-url>/earning-robot:latest
docker push <ecr-url>/earning-robot:latest
```

### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/<project-id>/earning-robot
gcloud run deploy --image gcr.io/<project-id>/earning-robot
```

### Azure Container Instances

```bash
# Build and push to ACR
az acr build --registry <registry> --image earning-robot:latest .
az container create --resource-group <rg> --name robot --image <registry>.azurecr.io/earning-robot:latest
```

## Support

For Docker-specific issues:
- Check container logs
- Verify .env configuration
- Ensure ports are available
- Check Docker daemon status
