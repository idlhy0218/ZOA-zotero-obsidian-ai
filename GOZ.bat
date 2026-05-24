@echo off
cd /d "%~dp0"

:: Try running with 'python' from PATH
python goz.py 2>nul
if %errorlevel% equ 0 goto :end

:: Fallback: try 'py' launcher (Windows Python Launcher)
py goz.py 2>nul
if %errorlevel% equ 0 goto :end

:: Neither worked
echo.
echo  [Error] Python was not found.
echo  Please install Python from https://www.python.org/downloads/
echo  and make sure to check "Add Python to PATH" during installation.
echo.
pause

:end
