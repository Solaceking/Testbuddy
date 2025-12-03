@echo off
REM build_windows.bat - Create a single-file TestBuddy.exe and (optionally) compile NSIS installer
REM Usage: run from project root in an elevated PowerShell/Command Prompt with the venv activated

SETLOCAL

REM Activate venv if present
if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
) else (
  echo Warning: virtualenv not found at .venv\Scripts\activate.bat. Ensure dependencies are installed.
)

REM Ensure PyInstaller is installed
python -m pip install --upgrade pip
python -m pip install pyinstaller

REM Build the executable
REM Output to ./dist to match packaging expectations
pyinstaller --noconfirm --onefile --windowed --name TestBuddy --icon icon.ico --distpath dist app.py

IF ERRORLEVEL 1 (
  echo PyInstaller failed. See output above.
  exit /b 1
)

REM If NSIS (makensis) is available, compile the installer
where makensis >nul 2>&1
if %ERRORLEVEL%==0 (
  echo Found makensis, compiling NSIS installer...
  makensis testbuddy_installer.nsi
  if ERRORLEVEL 1 (
    echo NSIS failed to compile the installer.
  ) else (
    echo NSIS installer created successfully.
  )
) else (
  echo makensis (NSIS) not found in PATH - skipping installer compilation.
  echo You can install NSIS and re-run this script to create the installer.
)

echo Build complete. Output folder: %CD%\dist
ENDLOCAL
pause
