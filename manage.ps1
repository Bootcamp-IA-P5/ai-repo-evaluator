# PowerShell version of manage.sh
# Usage: .\manage.ps1 {db|backend|all|rebuild|stop|backup|restore|logs}

param(
    [Parameter(Position=0)]
    [ValidateSet("db", "backend", "all", "rebuild", "stop", "backup", "restore", "logs")]
    [string]$Command
)

# --- Command Detection ---
$DOCKER_CMD = $null
if (docker compose version 2>&1) {
    $DOCKER_CMD = "docker compose"
} elseif (docker-compose version 2>&1) {
    $DOCKER_CMD = "docker-compose"
} else {
    Write-Host "❌ Error: Neither 'docker compose' nor 'docker-compose' was found." -ForegroundColor Red
    exit 1
}

$COMPOSE_FILE = "docker-compose.dev.yml"
$BACKUP_DIR = ".\backups"

# Function to load environment variables from .env file
function Get-EnvVariables {
    $envPath = ".\backend\.env"
    if (Test-Path $envPath) {
        Get-Content $envPath | ForEach-Object {
            if ($_ -match "^([^#][^=]+)=(.*)$") {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                # Remove surrounding quotes if present
                if ($value -match '^"(.*)"$' -or $value -match "^'(.*)'$") {
                    $value = $matches[1]
                }
                Set-Item -Path "env:$name" -Value $value -Force
            }
        }
    }
}

# Load environment variables
Get-EnvVariables

# Create backup directory if it doesn't exist
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
}

# Execute command
switch ($Command) {
    "db" {
        Write-Host "🚀 Starting Database service..." -ForegroundColor Cyan
        Invoke-Expression "$DOCKER_CMD -f $COMPOSE_FILE up -d db"
    }
    "backend" {
        Write-Host "🚀 Starting Database and Backend services..." -ForegroundColor Cyan
        Invoke-Expression "$DOCKER_CMD -f $COMPOSE_FILE up -d backend"
    }
    "all" {
        Write-Host "🚀 Starting all services..." -ForegroundColor Cyan
        Invoke-Expression "$DOCKER_CMD -f $COMPOSE_FILE up -d"
    }
    "rebuild" {
        Write-Host "♻️  Rebuilding all images from scratch (no-cache)..." -ForegroundColor Yellow
        Invoke-Expression "$DOCKER_CMD -f $COMPOSE_FILE build --no-cache"
        Write-Host "🚀 Restarting services..." -ForegroundColor Cyan
        Invoke-Expression "$DOCKER_CMD -f $COMPOSE_FILE up -d"
    }
    "stop" {
        Write-Host "🛑 Stopping all services..." -ForegroundColor Red
        Invoke-Expression "$DOCKER_CMD -f $COMPOSE_FILE down"
    }
    "backup" {
        $FILENAME = Read-Host "📂 Enter backup filename"
        if (-not $FILENAME.EndsWith(".sql")) {
            $FILENAME += ".sql"
        }
        $FULL_PATH = Join-Path $BACKUP_DIR $FILENAME
        docker exec -t evaluator_db pg_dump -U $env:POSTGRES_USER $env:POSTGRES_DB | Out-File -FilePath $FULL_PATH -Encoding utf8
        Write-Host "✅ Backup complete: $FULL_PATH" -ForegroundColor Green
    }
    "restore" {
        Write-Host "📂 Available backups:" -ForegroundColor Cyan
        Get-ChildItem $BACKUP_DIR | ForEach-Object { Write-Host "  $($_.Name)" }
        $FILENAME = Read-Host "📥 Filename to restore"
        $FULL_PATH = Join-Path $BACKUP_DIR $FILENAME
        if (Test-Path $FULL_PATH) {
            Get-Content $FULL_PATH | docker exec -i evaluator_db psql -U $env:POSTGRES_USER -d $env:POSTGRES_DB
            Write-Host "✅ Restore complete!" -ForegroundColor Green
        } else {
            Write-Host "❌ Error: File not found." -ForegroundColor Red
        }
    }
    "logs" {
        Invoke-Expression "$DOCKER_CMD -f $COMPOSE_FILE logs -f"
    }
    default {
        Write-Host "Usage: .\manage.ps1 {db|backend|all|rebuild|stop|backup|restore|logs}" -ForegroundColor Yellow
        exit 1
    }
}