#!/usr/bin/env python3
"""
TestBuddy v2 Application Launcher

Runs the TestBuddy OCR workbench with proper initialization and error handling.
"""

import sys
import os
from pathlib import Path

# Ensure project directory is in path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def check_dependencies():
    """Verify all required dependencies are installed."""
    print("Checking dependencies...")
    
    required = {
        'PyQt6': 'PyQt6.QtCore',
        'Pillow': 'PIL',
        'pytesseract': 'pytesseract',
    }
    
    missing = []
    for name, module in required.items():
        try:
            __import__(module)
            print(f"  [OK] {name}")
        except ImportError:
            print(f"  [MISSING] {name} - NOT INSTALLED")
            missing.append(name)
    
    if missing:
        print(f"\nWarning: Missing dependencies: {', '.join(missing)}")
        print("\nInstall with:")
        print(f"  pip install -r requirements.txt")
        return False
    
    print("\nAll dependencies installed!\n")
    return True


def check_tesseract():
    """Verify Tesseract OCR is installed."""
    print("Checking Tesseract OCR...")
    from config import ConfigManager
    
    cm = ConfigManager()
    tesseract_path = cm.config.tesseract_path
    
    if Path(tesseract_path).exists():
        print(f"  [OK] Found: {tesseract_path}")
        return True
    else:
        print(f"  [WARNING] Tesseract not found at: {tesseract_path}")
        print("\nDownload and install from:")
        print("  https://github.com/UB-Mannheim/tesseract/wiki")
        print("\nOr update tesseract_path in testbuddy.ini")
        return False


def main():
    """Launch the app."""
    print("=" * 60)
    print("TestBuddy v2 - Document OCR Workbench")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\nError: missing dependencies")
        return 1
    
    # Check Tesseract (warning only)
    tesseract_ok = check_tesseract()
    if not tesseract_ok:
        print("\nWarning: Tesseract not available")
        print("   The app will start but OCR capture will fail\n")
    
    # Import and run app
    print("Starting TestBuddy v2...\n")
    try:
        from app import main as app_main
        app_main()
        return 0
    except KeyboardInterrupt:
        print("\n\nApp closed by user")
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
