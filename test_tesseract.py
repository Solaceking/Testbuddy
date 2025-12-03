"""
Tesseract Diagnostic Tool
=========================

This script checks your Tesseract installation and helps diagnose issues.
Run this to see exactly what's wrong with your OCR setup.
"""

import sys
import os
from pathlib import Path

print("=" * 80)
print("TESSERACT DIAGNOSTIC TOOL")
print("=" * 80)
print()

# Step 1: Check if pytesseract is installed
print("[1/6] Checking pytesseract package...")
try:
    import pytesseract
    print("     ✓ pytesseract is installed")
except ImportError as e:
    print("     ✗ pytesseract is NOT installed")
    print(f"     Error: {e}")
    print()
    print("     FIX: Run this command:")
    print("     pip install pytesseract")
    sys.exit(1)

# Step 2: Check if Pillow is installed
print()
print("[2/6] Checking Pillow (PIL) package...")
try:
    from PIL import Image
    print("     ✓ Pillow is installed")
except ImportError as e:
    print("     ✗ Pillow is NOT installed")
    print(f"     Error: {e}")
    print()
    print("     FIX: Run this command:")
    print("     pip install Pillow")
    sys.exit(1)

# Step 3: Check common Tesseract paths
print()
print("[3/6] Searching for Tesseract binary...")

possible_paths = [
    Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
    Path(r"C:\Tesseract-OCR\tesseract.exe"),
    Path(r"C:\Users") / os.environ.get('USERNAME', '') / "AppData" / "Local" / "Programs" / "Tesseract-OCR" / "tesseract.exe",
]

tesseract_found = None
for path in possible_paths:
    if path.exists():
        print(f"     ✓ Found at: {path}")
        tesseract_found = path
        break
    else:
        print(f"     ✗ Not found at: {path}")

if not tesseract_found:
    print()
    print("     " + "=" * 70)
    print("     TESSERACT NOT FOUND!")
    print("     " + "=" * 70)
    print()
    print("     You need to install Tesseract OCR:")
    print()
    print("     1. Download installer from:")
    print("        https://github.com/UB-Mannheim/tesseract/wiki")
    print()
    print("     2. Run the installer")
    print()
    print("     3. Use default installation path:")
    print("        C:\\Program Files\\Tesseract-OCR")
    print()
    print("     4. Run this diagnostic again")
    print()
    sys.exit(1)

# Step 4: Configure pytesseract to use found path
print()
print("[4/6] Configuring pytesseract...")
pytesseract.pytesseract.tesseract_cmd = str(tesseract_found)
print(f"     ✓ Set tesseract path to: {tesseract_found}")

# Step 5: Try to get Tesseract version
print()
print("[5/6] Testing Tesseract executable...")
try:
    version = pytesseract.get_tesseract_version()
    print(f"     ✓ Tesseract version: {version}")
except Exception as e:
    print(f"     ✗ Failed to run Tesseract")
    print(f"     Error: {e}")
    print()
    print("     Possible issues:")
    print("     - Tesseract installation is corrupted")
    print("     - Missing Visual C++ Redistributable")
    print("     - Permission issues")
    print()
    print("     Try:")
    print("     1. Reinstall Tesseract")
    print("     2. Install Visual C++ Redistributable:")
    print("        https://aka.ms/vs/17/release/vc_redist.x64.exe")
    sys.exit(1)

# Step 6: Try a simple OCR test
print()
print("[6/6] Testing OCR functionality...")
try:
    # Create a simple test image with text
    from PIL import Image, ImageDraw, ImageFont
    
    # Create white image with black text
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 30), "TEST 123", fill='black', font=font)
    
    # Try OCR
    text = pytesseract.image_to_string(img)
    text = text.strip()
    
    if text:
        print(f"     ✓ OCR test successful!")
        print(f"     Detected text: '{text}'")
    else:
        print(f"     ⚠ OCR ran but detected no text")
        print(f"     This might be normal - try with a real screenshot")
        
except Exception as e:
    print(f"     ✗ OCR test failed")
    print(f"     Error: {e}")
    print()
    import traceback
    print("     Full error:")
    print("     " + "-" * 70)
    traceback.print_exc()
    print("     " + "-" * 70)
    sys.exit(1)

# Success!
print()
print("=" * 80)
print("✓ ALL CHECKS PASSED!")
print("=" * 80)
print()
print("Your Tesseract installation is working correctly.")
print()
print("Configuration for testbuddy.ini:")
print(f"  tesseract_path = {tesseract_found}")
print()
print("You can now use TestBuddy OCR features!")
print()
print("=" * 80)
