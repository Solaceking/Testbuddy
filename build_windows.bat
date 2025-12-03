@echo off
REM ============================================================
REM TestBuddy Windows Build Script
REM ============================================================
REM This script builds the TestBuddy Windows executable using
REM PyInstaller. Run this on a Windows machine with Python 3.10+
REM
REM Prerequisites:
REM   1. Python 3.10+ installed
REM   2. All dependencies installed: pip install -r requirements.txt
REM   3. PyInstaller installed: pip install pyinstaller
REM
REM Usage:
REM   Double-click this file or run: build_windows.bat
REM ============================================================

echo ===== TestBuddy Windows Build Script =====
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ and try again
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python --version

echo.
echo [2/5] Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [3/5] Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo.
echo [4/5] Building TestBuddy.exe with PyInstaller...
echo This may take 2-5 minutes...
pyinstaller testbuddy.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo [5/5] Verifying output...
if exist dist\TestBuddy.exe (
    echo SUCCESS! TestBuddy.exe created in dist\ folder
    echo.
    echo File size:
    dir dist\TestBuddy.exe | find "TestBuddy.exe"
    echo.
    echo ===== Build Complete! =====
    echo.
    echo Next steps:
    echo   1. Test: dist\TestBuddy.exe
    echo   2. Create installer: Right-click testbuddy_installer.nsi ^> Compile NSIS Script
    echo   3. Distribute: TestBuddy-Setup.exe
) else (
    echo ERROR: TestBuddy.exe not found in dist\ folder
    pause
    exit /b 1
)

echo.
pause
