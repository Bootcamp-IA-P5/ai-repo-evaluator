# Deployment Infrastructure Plan - Dev/Test vs Production

> **Status**: Planned (Not Yet Implemented)
> **Created**: 2026-02-26
> **Last Updated**: 2026-02-26

---

## Overview

Create separate deployment configurations for dev/test and production environments with proper separation of concerns, optimized images, and multi-architecture support.

---

## Decisions Made

| Decision | Choice | Notes |
|----------|--------|-------|
| Docker Hub Repository | `osrogon` | Default repository for push command |
| Version Tagging | `latest` only | No version numbers, just latest tag |
| Production Database | Containerized PostgreSQL | Same as dev, with persistent volume |
| Nginx/Reverse Proxy | Not needed | Server already has nginx |
| Resource Limits | Yes | Sensible defaults included |
| External Network | `nginx_proxy_network` | Pre-existing network on server |

---

## Files to Create (7 new files)

### 1. `backend/requirements.dev.txt`

Development/test dependencies that extend the base requirements.

```
-r requirements.txt
pytest==8.0.0
pytest-cov==4.1.0
```

### 2. `backend/requirements.prod.txt`

Production optimizations that extend the base requirements.

```
-r requirements.txt
uvloop==0.19.0
```

### 3. `backend/.dockerignore`

Exclude unnecessary files from Docker build context.

```
__pycache__
*.pyc
*.pyo
.git
.gitignore
.env
.env.*
.venv
venv
ENV
pytest_cache
.coverage
htmlcov
*.log
tests/
*.md
Dockerfile*
```

### 4. `backend/Dockerfile.prod`

Multi-stage production build with optimizations.

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.prod.txt requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runner
FROM python:3.11-slim as runner

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvloop for better performance
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5. `frontend/Dockerfile.prod`

Multi-stage Next.js production build.

```dockerfile
# Stage 1: Builder
FROM node:20-slim as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including devDependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Runner
FROM node:20-slim as runner

WORKDIR /app

# Set to production
ENV NODE_ENV=production

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy built application
COPY --from=builder --chown=appuser:appuser /app/.next/standalone ./
COPY --from=builder --chown=appuser:appuser /app/.next/static ./.next/static
COPY --from=builder --chown=appuser:appuser /app/public ./public

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start the application
CMD ["node", "server.js"]
```

### 6. `docker-compose.prod.yml`

Production orchestration with external network and resource limits.

```yaml
services:
  db:
    image: postgres:15-alpine
    container_name: evaluator_db_prod
    restart: always
    env_file:
      - ./backend/.env.prod
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
    networks:
      - nginx_proxy_network
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: evaluator_backend_prod
    restart: always
    env_file:
      - ./backend/.env.prod
    depends_on:
      db:
        condition: service_healthy
    networks:
      - nginx_proxy_network
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: evaluator_frontend_prod
    restart: always
    env_file:
      - ./frontend/.env.prod
    depends_on:
      - backend
    networks:
      - nginx_proxy_network
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  nginx_proxy_network:
    external: true

volumes:
  postgres_data_prod:
```

### 7. `backend/.env.prod.template`

Production environment template.

```env
# PostgreSQL Credentials (set real values in deployment)
POSTGRES_USER=<production-user>
POSTGRES_PASSWORD=<secure-password>
POSTGRES_DB=evaluador_db
DB_HOST=db
DB_PORT=5432

# Assembled Connection String (optional)
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${DB_HOST}:${DB_PORT}/${POSTGRES_DB}

# AI / RAG Configuration
OPENAI_API_KEY=<your-openai-key>
GEMINI_API_KEY=<your-gemini-key>

# Production Settings
ENVIRONMENT=production
LOG_LEVEL=INFO

# API Configuration (defaults shown)
# API_V1_PREFIX=/api/v1
# APP_TITLE=Evaluador RAG API
# APP_DESCRIPTION=Automated GitHub Repository Grading with RAG
# APP_VERSION=1.0.0
```

---

## Files to Modify (4 files)

### 1. `backend/requirements.txt`

**Remove** dev dependencies (move to requirements.dev.txt):
- `pytest==8.0.0`
- `pytest-cov==4.1.0`

**Final content:**
```
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.7

# Database (PostgreSQL)
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# AI & RAG (Core for Dev B)
GitPython==3.1.43
langchain==0.1.9
langchain-community==0.0.24
langchain-openai==0.0.8
faiss-cpu==1.7.4
pypdf==4.0.1
tiktoken==0.6.0

# Environment & Utils
colorlog==6.8.2
python-dotenv==1.0.1
requests==2.31.0
pydantic-settings==2.1.0
```

### 2. `backend/Dockerfile.dev`

**Change** the requirements file reference:

```diff
- COPY requirements.txt .
- RUN pip install --no-cache-dir -r requirements.txt
+ COPY requirements.dev.txt requirements.txt ./
+ RUN pip install --no-cache-dir -r requirements.dev.txt
```

### 3. `frontend/Dockerfile.dev`

No changes needed - current setup is correct for development.

### 4. `manage.sh`

Add the following new command cases:

```bash
  prod)
    echo "🚀 Starting all services (Production)..."
    $DOCKER_CMD -f docker-compose.prod.yml up -d
    ;;

  rebuild-prod)
    echo "♻️  Rebuilding production images from scratch (no-cache)..."
    $DOCKER_CMD -f docker-compose.prod.yml build --no-cache
    echo "🚀 Restarting production services..."
    $DOCKER_CMD -f docker-compose.prod.yml up -d
    ;;

  stop-prod)
    echo "🛑 Stopping production services..."
    $DOCKER_CMD -f docker-compose.prod.yml down
    ;;

  logs-prod)
    $DOCKER_CMD -f docker-compose.prod.yml logs -f
    ;;

  push)
    REPO=${2:-osrogon}
    echo "🔨 Building and pushing multi-arch images (AMD64 + ARM64)..."
    
    # Ensure buildx is available and builder is set up
    docker buildx create --use --name multiarch_builder 2>/dev/null || docker buildx use multiarch_builder
    
    # Backend
    echo "📦 Building and pushing backend image..."
    docker buildx build --platform linux/amd64,linux/arm64 \
        -t $REPO/ai-repo-evaluator-backend:latest \
        -f backend/Dockerfile.prod \
        --push backend
    
    # Frontend
    echo "📦 Building and pushing frontend image..."
    docker buildx build --platform linux/amd64,linux/arm64 \
        -t $REPO/ai-repo-evaluator-frontend:latest \
        -f frontend/Dockerfile.prod \
        --push frontend
    
    echo "✅ Images pushed to Docker Hub: $REPO"
    echo "   - $REPO/ai-repo-evaluator-backend:latest"
    echo "   - $REPO/ai-repo-evaluator-frontend:latest"
    ;;

  backup-prod)
    read -p "📂 Enter backup filename: " FILENAME
    FULL_PATH="$BACKUP_DIR/$FILENAME.sql"
    docker exec -t evaluator_db_prod pg_dump -U $POSTGRES_USER $POSTGRES_DB > "$FULL_PATH"
    echo "✅ Backup complete: $FULL_PATH"
    ;;

  restore-prod)
    echo "📂 Available backups:"
    ls $BACKUP_DIR
    read -p "📥 Filename to restore: " FILENAME
    FULL_PATH="$BACKUP_DIR/$FILENAME"
    if [ -f "$FULL_PATH" ]; then
        cat "$FULL_PATH" | docker exec -i evaluator_db_prod psql -U $POSTGRES_USER -d $POSTGRES_DB
        echo "✅ Restore complete!"
    else
        echo "❌ Error: File not found."
    fi
    ;;
```

**Update the usage message:**

```bash
  *)
    echo "Usage: $0 {db|backend|all|prod|rebuild|rebuild-prod|stop|stop-prod|backup|restore|logs|logs-prod|push [repo]}"
    exit 1
```

---

## Complete Commands Reference

| Command | Environment | Description |
|---------|-------------|-------------|
| `db` | dev | Start database only |
| `backend` | dev | Start db + backend |
| `all` | dev | Start all services |
| `prod` | **prod** | Start all services |
| `rebuild` | dev | Rebuild dev images (no-cache) |
| `rebuild-prod` | **prod** | Rebuild prod images (no-cache) |
| `stop` | dev | Stop dev services |
| `stop-prod` | **prod** | Stop production services |
| `logs` | dev | View dev logs |
| `logs-prod` | **prod** | View production logs |
| `backup` | dev | Create database backup |
| `backup-prod` | **prod** | Create production database backup |
| `restore` | dev | Restore database |
| `restore-prod` | **prod** | Restore production database |
| `push [repo]` | - | Push multi-arch images to Docker Hub (default: osrogon) |

---

## Implementation Order

1. [ ] Create `backend/requirements.dev.txt`
2. [ ] Create `backend/requirements.prod.txt`
3. [ ] Update `backend/requirements.txt` (remove pytest, pytest-cov)
4. [ ] Create `backend/.dockerignore`
5. [ ] Create `backend/Dockerfile.prod`
6. [ ] Update `backend/Dockerfile.dev`
7. [ ] Create `frontend/Dockerfile.prod`
8. [ ] Create `docker-compose.prod.yml`
9. [ ] Create `backend/.env.prod.template`
10. [ ] Update `manage.sh` with all new commands
11. [ ] (Optional) Update `manage.ps1` and `manage.bat`

---

## Prerequisites for Production Deployment

1. **Docker Buildx** - For multi-architecture builds
   ```bash
   docker buildx create --name multiarch_builder --use
   docker buildx inspect --bootstrap
   ```

2. **Docker Hub Login** - For pushing images
   ```bash
   docker login
   ```

3. **External Network** - Ensure `nginx_proxy_network` exists on server
   ```bash
   docker network create nginx_proxy_network
   ```

4. **Production Environment Files** - Create `.env.prod` files from templates

---

## Notes

- The `GitPython` requirement had a space in the version (`GitPython ==3.1.43`) - should be fixed to `GitPython==3.1.43`
- Frontend prod Dockerfile requires Next.js standalone output mode - may need to update `next.config.ts`
- Resource limits can be adjusted based on actual server capacity