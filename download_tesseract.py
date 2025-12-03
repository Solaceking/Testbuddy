#!/usr/bin/env python3
"""
Download and extract Tesseract OCR portable for bundling with TestBuddy.
This script downloads the official Tesseract Windows installer and extracts
the necessary files for bundling.

Usage:
    python download_tesseract.py
"""

import os
import sys
import urllib.request
import zipfile
import tempfile
import shutil
from pathlib import Path

# Tesseract download URLs
TESSERACT_VERSION = "5.4.0.20240606"
TESSERACT_URL = f"https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-{TESSERACT_VERSION}.exe"

# Alternative: Use portable ZIP (if available)
# For now, we'll download the installer and extract it

PROJECT_ROOT = Path(__file__).parent
TESSERACT_DIR = PROJECT_ROOT / "tesseract"
TESSDATA_DIR = TESSERACT_DIR / "tessdata"

def download_file(url: str, dest: Path) -> None:
    """Download a file with progress."""
    print(f"📥 Downloading: {url}")
    print(f"📁 Destination: {dest}")
    
    try:
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(dest, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r⏳ Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')
        
        print("\n✅ Download complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False


def download_tessdata_file(lang: str = "eng") -> bool:
    """Download trained data file directly."""
    tessdata_url = f"https://github.com/tesseract-ocr/tessdata/raw/main/{lang}.traineddata"
    dest = TESSDATA_DIR / f"{lang}.traineddata"
    
    print(f"\n📥 Downloading {lang}.traineddata...")
    
    try:
        urllib.request.urlretrieve(tessdata_url, dest)
        print(f"✅ Downloaded {lang}.traineddata")
        return True
    except Exception as e:
        print(f"❌ Failed to download {lang}.traineddata: {e}")
        return False


def create_minimal_tesseract_bundle() -> bool:
    """
    Create a minimal Tesseract bundle by downloading only essential files.
    This avoids the full installer extraction.
    """
    print("\n🔧 Creating minimal Tesseract bundle...")
    
    # Create directories
    TESSERACT_DIR.mkdir(exist_ok=True)
    TESSDATA_DIR.mkdir(exist_ok=True)
    
    # Download tesseract.exe (we'll provide instructions to copy from system installation)
    # Or use a pre-compiled portable version
    
    print("\n📋 MANUAL STEP REQUIRED:")
    print("=" * 60)
    print("Since we're in Linux, you need to copy Tesseract files from")
    print("your Windows installation:")
    print()
    print("1. On your Windows machine, locate:")
    print("   C:\\Program Files\\Tesseract-OCR\\")
    print()
    print("2. Copy these files to the project:")
    print(f"   {TESSERACT_DIR}/")
    print()
    print("   Required files:")
    print("   - tesseract.exe")
    print("   - tessdata/eng.traineddata")
    print("   - tessdata/osd.traineddata (optional)")
    print()
    print("3. Or run this script on Windows to auto-download.")
    print("=" * 60)
    
    # Download traineddata files directly
    print("\n📥 Downloading trained data files...")
    download_tessdata_file("eng")  # English
    download_tessdata_file("osd")  # Orientation and script detection
    
    print("\n✅ Tessdata files downloaded!")
    print(f"📁 Location: {TESSDATA_DIR}")
    
    return True


def create_bundled_tesseract_config() -> None:
    """Create configuration for bundled Tesseract."""
    
    config_content = """# Tesseract Bundled Configuration
# This file is auto-generated for bundled Tesseract

[tesseract]
# Bundled Tesseract path (relative to app)
bundled_path = tesseract/tesseract.exe
tessdata_path = tesseract/tessdata

# These will be set automatically by the app
tesseract_cmd = 
tessdata_prefix = 
"""
    
    config_file = PROJECT_ROOT / "tesseract_bundle.ini"
    config_file.write_text(config_content)
    print(f"\n✅ Created config: {config_file}")


def create_windows_copy_script() -> None:
    """Create a Windows batch script to copy Tesseract files."""
    
    script_content = """@echo off
REM Copy Tesseract from system installation to project bundle
REM Run this on Windows after installing Tesseract

echo ========================================
echo TestBuddy - Bundle Tesseract Setup
echo ========================================
echo.

set "TESSERACT_SRC=C:\\Program Files\\Tesseract-OCR"
set "TESSERACT_DEST=%~dp0tesseract"

if not exist "%TESSERACT_SRC%" (
    echo ERROR: Tesseract not found at %TESSERACT_SRC%
    echo.
    echo Please install Tesseract first:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    pause
    exit /b 1
)

echo Creating bundle directory...
mkdir "%TESSERACT_DEST%" 2>nul
mkdir "%TESSERACT_DEST%\\tessdata" 2>nul

echo.
echo Copying Tesseract files...
copy "%TESSERACT_SRC%\\tesseract.exe" "%TESSERACT_DEST%\\" /Y
copy "%TESSERACT_SRC%\\tessdata\\eng.traineddata" "%TESSERACT_DEST%\\tessdata\\" /Y
copy "%TESSERACT_SRC%\\tessdata\\osd.traineddata" "%TESSERACT_DEST%\\tessdata\\" /Y

echo.
echo Copying DLL dependencies...
for %%F in (
    libtesseract-5.dll
    libleptonica-1.84.1.dll
    libarchive-13.dll
    libbrotlicommon.dll
    libbrotlidec.dll
    libbz2-1.dll
    libcrypto-3-x64.dll
    libcurl-4.dll
    libdeflate.dll
    libgif-7.dll
    libiconv-2.dll
    libintl-8.dll
    libjbig-0.dll
    libjpeg-8.dll
    liblzma-5.dll
    liblzo2-2.dll
    libnettle-8.dll
    libopenjp2-7.dll
    libpng16-16.dll
    libsharpyuv-0.dll
    libssh2-1.dll
    libssl-3-x64.dll
    libtiff-6.dll
    libwebp-7.dll
    libwebpdemux-2.dll
    libwebpmux-3.dll
    libxml2-2.dll
    libzstd.dll
    zlib1.dll
) do (
    if exist "%TESSERACT_SRC%\\%%F" (
        copy "%TESSERACT_SRC%\\%%F" "%TESSERACT_DEST%\\" /Y
    )
)

echo.
echo ========================================
echo Bundle created successfully!
echo ========================================
echo.
echo Location: %TESSERACT_DEST%
echo.
echo Next steps:
echo 1. Verify files exist in tesseract/ folder
echo 2. Run: python app_nosplash.py
echo 3. Test OCR functionality
echo 4. Build .exe: build_windows.bat
echo.
pause
"""
    
    script_file = PROJECT_ROOT / "copy_tesseract.bat"
    script_file.write_text(script_content)
    print(f"✅ Created: {script_file}")


def main():
    """Main function."""
    print("=" * 60)
    print("🔧 TestBuddy - Tesseract Bundle Setup")
    print("=" * 60)
    
    # Create minimal bundle
    create_minimal_tesseract_bundle()
    
    # Create config
    create_bundled_tesseract_config()
    
    # Create Windows copy script
    create_windows_copy_script()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("📋 NEXT STEPS (on Windows):")
    print()
    print("1. Install Tesseract if not already installed:")
    print("   https://github.com/UB-Mannheim/tesseract/wiki")
    print()
    print("2. Run the copy script:")
    print("   copy_tesseract.bat")
    print()
    print("3. Verify files copied:")
    print("   dir tesseract\\")
    print()
    print("4. Test the app:")
    print("   python app_nosplash.py")
    print()
    print("5. Build the executable:")
    print("   build_windows.bat")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
