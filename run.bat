@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python app.py
if errorlevel 1 (
    echo.
    echo [ERROR] App exited with an error. See above.
    pause
)
