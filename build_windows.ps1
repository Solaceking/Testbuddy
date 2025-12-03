# build_windows.ps1 - PowerShell helper to package TestBuddy
# Usage: Run from project root in an elevated PowerShell with the venv activated

param(
    [switch]$CompileNSIS
)

Write-Host "Activating virtual environment (if .venv exists)..."
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    & ".\.venv\Scripts\Activate.ps1"
} else {
    Write-Warning "Virtual environment not found at .venv. Continue if dependencies already installed."
}

Write-Host "Ensuring PyInstaller is installed..."
python -m pip install --upgrade pip
python -m pip install pyinstaller

Write-Host "Running PyInstaller..."
pyinstaller --noconfirm --onefile --windowed --name TestBuddy --icon icon.ico --distpath dist app.py
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed (exit code $LASTEXITCODE)"
}

if ($CompileNSIS) {
    Write-Host "Checking for makensis..."
    $makensis = Get-Command makensis -ErrorAction SilentlyContinue
    if ($null -ne $makensis) {
        Write-Host "Found makensis -> compiling NSIS installer"
        & makensis testbuddy_installer.nsi
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "NSIS compilation failed (exit code $LASTEXITCODE)"
        } else {
            Write-Host "NSIS installer created successfully."
        }
    } else {
        Write-Warning "makensis not found in PATH. Install NSIS and re-run with -CompileNSIS to produce installer."
    }
} else {
    Write-Host "Skipping NSIS compilation. Use -CompileNSIS to attempt compiling installer if makensis is available." 
}

Write-Host "Build complete. Output: $(Resolve-Path .\dist)"
