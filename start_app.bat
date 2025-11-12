@echo off
echo ========================================
echo Starting Multi-Agent Data Assistant
echo with MCP Integration
echo ========================================
echo.

REM Check if frontend .env exists
if not exist "frontend\.env" (
    echo [INFO] Creating frontend\.env from env.example...
    copy frontend\env.example frontend\.env
    echo [ACTION REQUIRED] Please edit frontend\.env with your Supabase credentials
    echo.
)

echo [1/2] Starting Backend API (Port 8010)...
echo.
start "Backend API" cmd /k "cd /d %~dp0 && .\venv\Scripts\Activate.ps1 && uvicorn server:app --host 0.0.0.0 --port 8010 --reload"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo [2/2] Starting Frontend (Port 8011)...
echo.
start "Frontend Dev Server" cmd /k "cd /d %~dp0\frontend && npm run dev -- --port 8011"

echo.
echo ========================================
echo Application Starting!
echo ========================================
echo.
echo Backend API: http://localhost:8010
echo API Docs:    http://localhost:8010/docs
echo Frontend:    http://localhost:8011
echo.
echo MCP Servers running internally:
echo   - db.query_supabase (Database queries)
echo   - email.send_report (Email sending)
echo.
echo Press any key to open the application...
pause >nul
start http://localhost:8011

