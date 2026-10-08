@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON=py"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo Python is not installed or is not available on PATH.
        goto :failed
    )
    set "PYTHON=python"
)

echo Installing the application and build dependencies...
%PYTHON% -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto :failed

echo Building TM-Allocator.exe...
%PYTHON% -m PyInstaller --clean --noconfirm interface.spec
if errorlevel 1 goto :failed

echo.
echo Build complete: dist\TM-Allocator.exe
pause
exit /b 0

:failed
echo.
echo Build failed. Check the messages above and make sure Python and internet access are available.
pause
exit /b 1
