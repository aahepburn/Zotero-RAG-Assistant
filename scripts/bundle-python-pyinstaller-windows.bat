@echo off
REM bundle-python-pyinstaller-windows.bat
REM Wrapper script to run the PowerShell bundle script
REM This creates a standalone Python bundle using PyInstaller for Windows

echo.
echo =========================================================================
echo  Zotero RAG Assistant - Windows Python Bundle Builder
echo =========================================================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PowerShell is not installed or not in PATH
    echo Please install PowerShell to run this script
    pause
    exit /b 1
)

REM Get the directory of this script
set SCRIPT_DIR=%~dp0
set PS_SCRIPT=%SCRIPT_DIR%bundle-python-pyinstaller-windows.ps1

REM Check if the PowerShell script exists
if not exist "%PS_SCRIPT%" (
    echo ERROR: PowerShell script not found: %PS_SCRIPT%
    pause
    exit /b 1
)

REM Run the PowerShell script with execution policy bypass
echo Running PowerShell bundle script...
echo.
powershell.exe -ExecutionPolicy Bypass -File "%PS_SCRIPT%"

REM Check the exit code
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo =========================================================================
    echo  ERROR: Bundle creation failed
    echo =========================================================================
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo =========================================================================
echo  Bundle creation completed successfully!
echo =========================================================================
echo.
pause
