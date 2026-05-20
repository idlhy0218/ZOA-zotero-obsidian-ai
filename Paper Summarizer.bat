@echo off
cd /d "%~dp0"
"C:\Users\User\AppData\Local\Python\pythoncore-3.14-64\python.exe" paper_summarizer.py
if %errorlevel% neq 0 (
    echo.
    echo Error occurred. Press any key to exit.
    pause >nul
)
