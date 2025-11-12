@echo off
echo ========================================
echo Push to GitHub Repository
echo ========================================
echo.
echo Repository: https://github.com/Gabriel-Kelvin/multiagent_mcp.git
echo.

REM Check if git is initialized
if not exist ".git" (
    echo Initializing Git repository...
    git init
    git remote add origin https://github.com/Gabriel-Kelvin/multiagent_mcp.git
    echo.
)

REM Check git status
echo Checking repository status...
git status
echo.

REM Ask for confirmation
set /p CONFIRM="Do you want to commit and push all changes? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled.
    exit /b 0
)

echo.
echo Adding all files...
git add .

echo.
set /p COMMIT_MSG="Enter commit message (or press Enter for default): "
if "%COMMIT_MSG%"=="" (
    set COMMIT_MSG=Update: Multi-Agent Data Assistant with MCP - Docker deployment ready
)

echo.
echo Committing with message: %COMMIT_MSG%
git commit -m "%COMMIT_MSG%"

echo.
echo Pushing to GitHub...
echo You will be prompted for your credentials:
echo   Username: Gabriel-Kelvin
echo   Password: [Your Personal Access Token]
echo.

git branch -M main
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Success! Code uploaded to GitHub
    echo ========================================
    echo.
    echo Repository URL: https://github.com/Gabriel-Kelvin/multiagent_mcp
    echo.
    echo Next steps:
    echo 1. Verify files on GitHub
    echo 2. Follow QUICKSTART_VM.md to deploy on your VM
    echo.
) else (
    echo.
    echo ========================================
    echo Error occurred during push
    echo ========================================
    echo.
    echo Common fixes:
    echo 1. Check your Personal Access Token
    echo 2. Ensure you have write access to the repository
    echo 3. Check internet connection
    echo.
    echo See GITHUB_UPLOAD_GUIDE.md for detailed help
    echo.
)

pause

