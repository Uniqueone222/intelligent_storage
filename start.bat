@echo off
REM ============================================================================
REM Intelligent Storage System - Quick Start Script (Windows)
REM ============================================================================
REM This script starts the entire application using Docker
REM Requires: Docker Desktop for Windows
REM ============================================================================

echo ================================================
echo   Intelligent Storage - Docker Quick Start
echo ================================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed
    echo Install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [OK] Docker is installed
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo [OK] Docker Desktop is running
echo.

REM Check for force flag
if "%1"=="-f" goto cleanup
if "%1"=="--force" goto cleanup
goto build

:cleanup
echo Stopping and removing existing containers...
docker-compose down -v
echo [OK] Cleaned up existing containers
echo.

:build
REM Build and start containers
echo Building Docker images...
echo This may take a few minutes on first run...
echo.

docker-compose build

if %errorlevel% neq 0 (
    echo [ERROR] Docker build failed
    pause
    exit /b 1
)

echo.
echo Starting all services...
echo.

docker-compose up -d

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)

echo.
echo [OK] All services started!
echo.

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 5 /nobreak >nul

REM Show service status
echo.
echo Service Status:
docker-compose ps

echo.
echo ================================================
echo   Application is ready!
echo ================================================
echo.
echo Access the application:
echo   File Browser:  http://localhost:8000/files/browse/
echo   Admin Panel:   http://localhost:8000/admin/
echo   API Docs:      http://localhost:8000/api/
echo   Health Check:  http://localhost:8000/api/health/
echo.
echo Useful commands:
echo   View logs:        docker-compose logs -f
echo   View backend:     docker-compose logs -f backend
echo   Stop services:    docker-compose stop
echo   Restart:          docker-compose restart
echo   Remove all:       docker-compose down -v
echo.
echo Note: First run will download Ollama models (3-5GB).
echo This happens automatically in the background.
echo.
echo Press any key to open the application in your browser...
pause >nul

start http://localhost:8000/files/browse/
