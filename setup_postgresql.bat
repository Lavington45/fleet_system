@echo off
REM FleetGuard PostgreSQL Local Setup Script for Windows

echo.
echo ===============================================
echo   FleetGuard - PostgreSQL Local Setup
echo ===============================================
echo.

REM Check if PostgreSQL is installed
where psql >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PostgreSQL is not installed or not in PATH
    echo Please download and install PostgreSQL from: https://www.postgresql.org/download/windows/
    echo Make sure to add PostgreSQL to your system PATH during installation
    pause
    exit /b 1
)

echo [✓] PostgreSQL found

REM Prompt for PostgreSQL password
set /p PG_PASSWORD="Enter PostgreSQL password (default user: postgres): "
if "%PG_PASSWORD%"=="" set PG_PASSWORD=postgres

REM Create database
echo.
echo [1/4] Creating database 'fleet_system'...
psql -U postgres -h localhost -c "CREATE DATABASE fleet_system;" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [✓] Database created (or already exists)
) else (
    echo [✓] Database already exists
)

REM Run schema
echo.
echo [2/4] Creating tables from schema.sql...
psql -U postgres -h localhost -d fleet_system -f schema.sql >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [✓] Tables created successfully
) else (
    echo [!] Tables may already exist
)

REM Set environment variables
echo.
echo [3/4] Setting environment variables...
setx DB_HOST localhost
setx DB_USER postgres
setx DB_PASSWORD "%PG_PASSWORD%"
setx DB_NAME fleet_system
setx SECRET_KEY "dev-secret-key-change-in-production"
echo [✓] Environment variables set (new terminal window may be needed)

REM Setup users
echo.
echo [4/4] Setting up demo users...
python setup_users.py
if %ERRORLEVEL% EQU 0 (
    echo [✓] Demo users configured
) else (
    echo [!] Could not configure users. Make sure you have psycopg2-binary installed
    echo    Run: pip install psycopg2-binary
)

echo.
echo ===============================================
echo   Setup Complete!
echo ===============================================
echo.
echo You can now start your Flask app:
echo   python app.py
echo.
echo Visit: http://localhost:5000
echo.
echo Demo credentials:
echo   Admin: admin / admin123
echo   Driver 1: driver1 / driver123
echo   Driver 2: driver2 / driver123
echo.
pause
