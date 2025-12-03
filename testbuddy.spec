# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for TestBuddy Native Windows Build
=========================================================

This spec file configures PyInstaller to create a standalone Windows
executable (.exe) that bundles all dependencies and resources.

Usage:
    pyinstaller testbuddy.spec

Output:
    dist/TestBuddy.exe - Single-file executable
"""

import sys
from pathlib import Path

block_cipher = None

# Define all Python modules to include
hiddenimports = [
    # Core dependencies
    'PIL',
    'PIL.Image',
    'PIL.ImageGrab',
    'pytesseract',
    'pyperclip',
    
    # PyQt6 modules
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    
    # Export modules
    'reportlab',
    'reportlab.lib',
    'reportlab.lib.pagesizes',
    'reportlab.lib.styles',
    'reportlab.platypus',
    'docx',
    'markdown',
    
    # Document Intelligence
    'cv2',
    'numpy',
    
    # Standard library
    'json',
    'datetime',
    'pathlib',
    'logging',
    'configparser',
]

# Collect data files (config templates, icons, etc.)
datas = [
    # Bundle Tesseract OCR
    ('tesseract/tesseract.exe', 'tesseract'),
    ('tesseract/tessdata', 'tesseract/tessdata'),
    # Note: tesseract DLL files will be added dynamically if found
]

# Check if tesseract directory exists and add DLL files
tesseract_dir = Path('tesseract')
if tesseract_dir.exists():
    # Add all DLL files from tesseract directory
    for dll_file in tesseract_dir.glob('*.dll'):
        datas.append((str(dll_file), 'tesseract'))
    print(f"✅ Found Tesseract bundle at: {tesseract_dir}")
    print(f"   Added {len(list(tesseract_dir.glob('*.dll')))} DLL files")
else:
    print("⚠️  Warning: tesseract/ directory not found. Run copy_tesseract.bat first!")

# Analysis: Find all imports and dependencies
a = Analysis(
    ['app.py'],  # Main entry point
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'scipy',
        'pandas',
        'tk',
        'tkinter',
        'unittest',
        'test',
        'tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ: Python archive
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# EXE: Executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TestBuddy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable with UPX
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if Path('icon.ico').exists() else None,  # Application icon
    version_file=None,  # Add version info later if needed
)

# Optional: Create a COLLECT (for --onedir mode)
# Uncomment if you want a directory distribution instead of single file
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='TestBuddy',
# )
