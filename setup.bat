@echo off
cd /d "%~dp0"

echo ============================================================
echo  WeChat Sender - Setup
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+ first.
    pause
    exit /b 1
)

if exist "venv\Scripts\activate.bat" (
    echo [OK] venv already exists, skipping.
    goto install
)

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create venv.
    pause
    exit /b 1
)
echo [OK] venv created.

:install
call venv\Scripts\activate.bat
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)
echo [OK] All dependencies installed.

echo.
echo ============================================================
echo  Setup complete! Run run.bat to start.
echo ============================================================
pause
