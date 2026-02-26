@echo off
REM Batch version of manage.sh
REM Usage: manage.bat {db|backend|all|rebuild|stop|backup|restore|logs}

setlocal enabledelayedexpansion

set COMPOSE_FILE=docker-compose.dev.yml
set BACKUP_DIR=.\backups

REM --- Command Detection ---
docker compose version >nul 2>&1
if %errorlevel% equ 0 (
    set DOCKER_CMD=docker compose
    goto :docker_found
)

docker-compose version >nul 2>&1
if %errorlevel% equ 0 (
    set DOCKER_CMD=docker-compose
    goto :docker_found
)

echo ❌ Error: Neither 'docker compose' nor 'docker-compose' was found.
exit /b 1

:docker_found

REM --- Load Environment Variables ---
if exist .\backend\.env (
    for /f "usebackq tokens=1,* delims==" %%a in (".\backend\.env") do (
        set "line=%%a"
        if "!line:~0,1!" neq "#" (
            set "%%a=%%b"
        )
    )
)

REM --- Create backup directory ---
if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

REM --- Parse Command ---
if "%1"=="" goto :usage
if "%1"=="db" goto :db
if "%1"=="backend" goto :backend
if "%1"=="all" goto :all
if "%1"=="rebuild" goto :rebuild
if "%1"=="stop" goto :stop
if "%1"=="backup" goto :backup
if "%1"=="restore" goto :restore
if "%1"=="logs" goto :logs
goto :usage

:db
echo 🚀 Starting Database service...
%DOCKER_CMD% -f %COMPOSE_FILE% up -d db
goto :eof

:backend
echo 🚀 Starting Database and Backend services...
%DOCKER_CMD% -f %COMPOSE_FILE% up -d backend
goto :eof

:all
echo 🚀 Starting all services...
%DOCKER_CMD% -f %COMPOSE_FILE% up -d
goto :eof

:rebuild
echo ♻️  Rebuilding all images from scratch (no-cache)...
%DOCKER_CMD% -f %COMPOSE_FILE% build --no-cache
echo 🚀 Restarting services...
%DOCKER_CMD% -f %COMPOSE_FILE% up -d
goto :eof

:stop
echo 🛑 Stopping all services...
%DOCKER_CMD% -f %COMPOSE_FILE% down
goto :eof

:backup
set /p FILENAME="📂 Enter backup filename: "
REM Add .sql extension if not present
echo %FILENAME% | findstr /r "\.sql$" >nul
if %errorlevel% neq 0 set FILENAME=%FILENAME%.sql
set FULL_PATH=%BACKUP_DIR%\%FILENAME%
docker exec -t evaluator_db pg_dump -U %POSTGRES_USER% %POSTGRES_DB% > "%FULL_PATH%"
echo ✅ Backup complete: %FULL_PATH%
goto :eof

:restore
echo 📂 Available backups:
dir /b %BACKUP_DIR%
set /p FILENAME="📥 Filename to restore: "
set FULL_PATH=%BACKUP_DIR%\%FILENAME%
if exist "%FULL_PATH%" (
    type "%FULL_PATH%" | docker exec -i evaluator_db psql -U %POSTGRES_USER% -d %POSTGRES_DB%
    echo ✅ Restore complete!
) else (
    echo ❌ Error: File not found.
)
goto :eof

:logs
%DOCKER_CMD% -f %COMPOSE_FILE% logs -f
goto :eof

:usage
echo Usage: %~nx0 {db^|backend^|all^|rebuild^|stop^|backup^|restore^|logs}
exit /b 1

endlocal