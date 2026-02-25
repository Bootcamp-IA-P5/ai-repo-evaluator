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
  logs)
    $DOCKER_CMD -f $COMPOSE_FILE logs -f
    ;;
  *)
    echo "Usage: $0 {db|backend|all|rebuild|stop|backup|restore|logs}"
    exit 1
esac