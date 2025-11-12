@echo off
REM Setup script for MCP Integration (Windows)

echo ==========================================
echo MCP Integration Setup
echo ==========================================
echo.

REM Check Python version
echo [1/4] Checking Python version...
python --version
echo.

REM Install dependencies
echo [2/4] Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    exit /b 1
)

REM Check if .env exists
echo.
echo [3/4] Checking environment configuration...
if not exist .env (
    echo Warning: .env file not found
    echo Copying env.example to .env...
    copy env.example .env
    echo Created .env file. Please edit it with your configuration.
) else (
    echo .env file exists
)

REM Test MCP integration
echo.
echo [4/4] Testing MCP servers...
python test_mcp_integration.py

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo MCP Integration Setup Complete!
    echo ==========================================
    echo.
    echo Next steps:
    echo 1. Configure your .env file with:
    echo    - Database credentials (DATA_DB_TYPE, DATA_DSN, etc.^)
    echo    - SendGrid API key (SENDGRID_API_KEY^)
    echo    - Email addresses (EMAIL_FROM, EMAIL_TO^)
    echo.
    echo 2. Start the server:
    echo    uvicorn server:app --host 0.0.0.0 --port 8010
    echo.
    echo 3. Or run directly:
    echo    python main.py
    echo.
) else (
    echo.
    echo MCP test encountered issues. Please check the output above.
    echo The app may still work, but MCP features might be limited.
)

pause

