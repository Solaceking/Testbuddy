#!/bin/bash
# ============================================================
# TestBuddy Windows Build Script (Linux/Mac cross-compile)
# ============================================================
# This script builds TestBuddy for Windows from Linux/Mac
# using Wine and PyInstaller.
#
# Prerequisites:
#   1. Wine installed: sudo apt-get install wine64
#   2. Python for Wine installed
#   3. PyInstaller for Wine installed
#
# Note: Native Windows build is recommended for best results.
#       Use build_windows.bat on Windows for production builds.
# ============================================================

set -e

echo "===== TestBuddy Cross-Platform Build Script ====="
echo ""

# Check if running on Windows (use .bat script instead)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Detected Windows. Please use build_windows.bat instead."
    exit 1
fi

echo "[1/5] Checking Python version..."
python3 --version

echo ""
echo "[2/5] Installing dependencies..."
pip3 install -q -r requirements.txt

echo ""
echo "[3/5] Cleaning previous builds..."
rm -rf dist/ build/ __pycache__/

echo ""
echo "[4/5] Building with PyInstaller..."
echo "This may take 2-5 minutes..."
pyinstaller testbuddy.spec

echo ""
echo "[5/5] Verifying output..."
if [ -f "dist/TestBuddy" ] || [ -f "dist/TestBuddy.exe" ]; then
    echo "SUCCESS! Executable created in dist/ folder"
    ls -lh dist/
    echo ""
    echo "===== Build Complete! ====="
    echo ""
    echo "Note: For Windows builds, it's recommended to build on"
    echo "a native Windows machine using build_windows.bat"
else
    echo "ERROR: Executable not found in dist/ folder"
    exit 1
fi
