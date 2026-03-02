#!/bin/bash

# --- Command Detection ---
if docker compose version >/dev/null 2>&1; then
    DOCKER_CMD="docker compose"
elif docker-compose version >/dev/null 2>&1; then
    DOCKER_CMD="docker-compose"
else
    echo "❌ Error: Neither 'docker compose' nor 'docker-compose' was found."
    exit 1
fi

COMPOSE_FILE="docker-compose.dev.yml"
BACKUP_DIR="./backups"

# Load Env Variables for Backup/Restore logic
if [ -f ./backend/.env ]; then
  export $(grep -v '^#' ./backend/.env | xargs)
fi

mkdir -p $BACKUP_DIR

case "$1" in
  db)
    echo "🚀 Starting Database service..."
    $DOCKER_CMD -f $COMPOSE_FILE up -d db
    ;;
  backend)
    echo "🚀 Starting Database and Backend services..."
    $DOCKER_CMD -f $COMPOSE_FILE up -d backend
    ;;
  all)
    echo "🚀 Starting all services..."
    $DOCKER_CMD -f $COMPOSE_FILE up -d
    ;;
  rebuild)
    echo "♻️  Rebuilding all images from scratch (no-cache)..."
    $DOCKER_CMD -f $COMPOSE_FILE build --no-cache
    echo "🚀 Restarting services..."
    $DOCKER_CMD -f $COMPOSE_FILE up -d
    ;;
  stop)
    echo "🛑 Stopping all services..."
    $DOCKER_CMD -f $COMPOSE_FILE down
    ;;
  backup)
    read -p "📂 Enter backup filename: " FILENAME
    FULL_PATH="$BACKUP_DIR/$FILENAME.sql"
    docker exec -t evaluator_db pg_dump -U $POSTGRES_USER $POSTGRES_DB > "$FULL_PATH"
    echo "✅ Backup complete: $FULL_PATH"
    ;;
  restore)
    echo "📂 Available backups:"
    ls $BACKUP_DIR
    read -p "📥 Filename to restore: " FILENAME
    FULL_PATH="$BACKUP_DIR/$FILENAME"
    if [ -f "$FULL_PATH" ]; then
        cat "$FULL_PATH" | docker exec -i evaluator_db psql -U $POSTGRES_USER -d $POSTGRES_DB
        echo "✅ Restore complete!"
    else
        echo "❌ Error: File not found."
    fi
    ;;
  restore-clean)
    echo "📂 Available backups:"
    ls $BACKUP_DIR
    read -p "📥 Filename to restore: " FILENAME
    FULL_PATH="$BACKUP_DIR/$FILENAME"
    if [ -f "$FULL_PATH" ]; then
        echo "🗑️  Dropping all tables..."
        docker exec -i evaluator_db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        echo "📥 Restoring from backup..."
        cat "$FULL_PATH" | docker exec -i evaluator_db psql -U $POSTGRES_USER -d $POSTGRES_DB
        echo "✅ Clean restore complete!"
    else
        echo "❌ Error: File not found."
    fi
    ;;
  truncate)
    echo "🗑️  Truncating all tables (keeping structure)..."
    docker exec -i evaluator_db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "TRUNCATE TABLE findings, evaluations, levels, criteria, rubrics CASCADE;"
    echo "✅ All tables truncated!"
    ;;
  reset-db)
    echo "🗑️  Dropping all tables..."
    docker exec -i evaluator_db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
    echo "🛠️  Recreating tables by restarting backend..."
    $DOCKER_CMD -f $COMPOSE_FILE restart backend
    echo "✅ Database reset complete!"
    ;;
  logs)
    $DOCKER_CMD -f $COMPOSE_FILE logs -f
    ;;
  push)
    REPO=${2:-osrogon}
    if [ -z "$2" ]; then
      read -p "📦 No repository specified. Use default 'osrogon'? [y/N]: " CONFIRM
      if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled. Usage: $0 push [repository]"
        exit 1
      fi
    fi
    
    echo "🔨 Building and pushing multi-arch images (AMD64 + ARM64) to $REPO..."
    
    # Ensure buildx is available
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
  *)
    echo "Usage: $0 {command}"
    echo ""
    echo "Commands:"
    echo "  db            Start Database service only"
    echo "  backend       Start Database and Backend services"
    echo "  all           Start all services"
    echo "  rebuild       Rebuild all images from scratch (no-cache)"
    echo "  stop          Stop all services"
    echo "  backup        Create a database backup"
    echo "  restore       Restore database from backup (keeps existing data)"
    echo "  restore-clean Restore database from backup (drops tables first)"
    echo "  truncate      Truncate all tables (keep structure, remove data)"
    echo "  reset-db      Drop and recreate all tables from models"
    echo "  logs          Follow container logs"
    echo "  push [repo]   Build and push multi-arch images to Docker Hub"
    exit 1
esac
