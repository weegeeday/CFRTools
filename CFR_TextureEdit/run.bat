@echo off
setlocal
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    echo [INFO] Starting Crazy Frog Texture Tool using virtual environment...
    start "" "venv\Scripts\python.exe" "gui_main.py"
    exit /b 0
)

echo [WARNING] Virtual environment not found. 
echo [INFO] Running with system python (this may fail if dependencies are missing).
echo [TIP] Run setup.bat first to install all requirements!
echo:

python "gui_main.py"

if %errorlevel% neq 0 (
    echo:
    echo [ERROR] Application failed to start.
    pause
)