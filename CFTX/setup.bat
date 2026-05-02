@echo off
setlocal
cd /d "%~dp0"

echo ======================================================
echo   Crazy Frog Texture Tool (CFTX) - Setup
echo ======================================================

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

:: Create Virtual Environment
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [INFO] Virtual environment already exists.
)

:: Install Requirements
echo [INFO] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Installation failed.
    pause
    exit /b 1
)

echo.
echo ======================================================
echo   Setup Complete!
echo   You can now run the tool using run.bat
echo ======================================================
echo.
pause
