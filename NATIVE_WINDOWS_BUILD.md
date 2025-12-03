# TestBuddy - Native Windows Build Guide
**Phase 3a: Windows Packaging & Distribution**  
**Date:** December 3, 2025  
**Status:** Build System Complete ✅

---

## Overview

This guide explains how to build TestBuddy as a native Windows executable (.exe) and create a professional installer. The process transforms the PyQt6 application into a standalone Windows program that runs without requiring Python installation.

---

## Prerequisites

### Required Software

1. **Windows 10 or Windows 11** (64-bit)
2. **Python 3.10 or higher**
   - Download: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
3. **Git** (for cloning repository)
   - Download: https://git-scm.com/download/win
4. **Tesseract OCR** (runtime dependency)
   - Download: https://github.com/UB-Mannheim/tesseract/wiki
   - Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

### Optional Software

5. **NSIS** (for creating installer)
   - Download: https://nsis.sourceforge.io/Download
   - Only needed if creating installer (.exe → setup.exe)
6. **Code Signing Certificate** (recommended for production)
   - Prevents "Unknown Publisher" warnings
   - Purchase from DigiCert, Sectigo, etc. (~$100/year)

---

## Quick Start (5 Minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/solaceking/Testbuddy.git
cd Testbuddy
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- PyQt6 (GUI framework)
- pytesseract, Pillow (OCR)
- reportlab, python-docx (export)
- opencv-python, numpy (document intelligence)
- **pyinstaller** (packaging)

### Step 3: Build Executable
```bash
# Option A: Use build script (easiest)
build_windows.bat

# Option B: Use PyInstaller directly
pyinstaller testbuddy.spec
```

**Output:** `dist/TestBuddy.exe` (~100-150 MB)

### Step 4: Test Executable
```bash
dist\TestBuddy.exe
```

Verify:
- ✅ Application launches without errors
- ✅ Can create new session
- ✅ Can capture screenshot (requires Tesseract)
- ✅ Can save/load sessions
- ✅ Export functionality works

---

## Detailed Build Instructions

### Method 1: Automated Build Script (Recommended)

```bash
# Run the automated build script
build_windows.bat
```

**What it does:**
1. Checks Python installation
2. Installs/updates dependencies
3. Cleans previous builds
4. Runs PyInstaller with testbuddy.spec
5. Verifies output

**Expected output:**
```
===== TestBuddy Windows Build Script =====
[1/5] Checking Python version...
Python 3.12.0
[2/5] Installing dependencies...
[3/5] Cleaning previous builds...
[4/5] Building TestBuddy.exe with PyInstaller...
[5/5] Verifying output...
SUCCESS! TestBuddy.exe created in dist\ folder
```

### Method 2: Manual PyInstaller Build

```bash
# Clean previous builds
rmdir /s /q dist build

# Run PyInstaller with spec file
pyinstaller testbuddy.spec

# Or create from scratch:
pyinstaller --onefile --windowed --name TestBuddy --icon icon.ico app.py
```

**PyInstaller Options:**
- `--onefile` - Single executable (vs. folder)
- `--windowed` - No console window (GUI app)
- `--name TestBuddy` - Output filename
- `--icon icon.ico` - Application icon
- `testbuddy.spec` - Configuration file (recommended)

---

## Creating the Windows Installer

### Prerequisites
- NSIS installed: https://nsis.sourceforge.io/Download
- TestBuddy.exe built in `dist/` folder

### Steps

1. **Verify TestBuddy.exe exists:**
   ```bash
   dir dist\TestBuddy.exe
   ```

2. **Create LICENSE.txt** (if not already present):
   - Already included in repository

3. **Compile NSIS script:**
   - Right-click `testbuddy_installer.nsi`
   - Select **"Compile NSIS Script"**
   - Wait for compilation (~10 seconds)

4. **Verify installer:**
   - Output: `TestBuddy-Setup.exe` (in project root)
   - Size: ~100-150 MB

5. **Test installer:**
   - Run `TestBuddy-Setup.exe`
   - Follow installation wizard
   - Verify shortcuts created:
     - Start Menu: `TestBuddy\TestBuddy.lnk`
     - Desktop: `TestBuddy.lnk`
   - Launch TestBuddy from Start Menu
   - Test all features

### Installer Features

✅ **Professional Install Wizard:**
- Welcome page
- License agreement (MIT License)
- Installation directory selection
- Progress bar
- Completion message with Tesseract reminder

✅ **Shortcuts:**
- Start Menu entry
- Desktop shortcut
- Uninstaller in Start Menu

✅ **Registry Entries:**
- Add/Remove Programs integration
- Uninstall information
- Application settings storage

✅ **File Associations** (optional):
- Uncomment lines in `.nsi` to associate `.testbuddy` files
- Right-click context menu "Open with TestBuddy"

---

## Application Icon

### Creating icon.ico

TestBuddy uses a Windows `.ico` file for the application icon. You have three options:

#### Option 1: Online Converter (Easiest)
1. Create a 256×256 PNG image with TestBuddy logo
2. Upload to: https://www.icoconverter.com/ or https://favicon-generator.org
3. Download as `icon.ico`
4. Place in project root: `Testbuddy/icon.ico`

#### Option 2: GIMP (Free Software)
1. Open/create image in GIMP
2. Scale to 256×256 (`Image → Scale Image`)
3. Export As → `icon.ico`
4. Select multiple sizes: 16, 32, 48, 128, 256

#### Option 3: ImageMagick (Command Line)
```bash
magick convert -resize 256x256 logo.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
```

### Using Without Icon

If `icon.ico` is missing:
- PyInstaller will build successfully (default Python icon used)
- NSIS will use default installer icon
- Application will still work perfectly

---

## Code Signing (Optional but Recommended)

### Why Code Sign?

❌ **Without signing:** Windows SmartScreen shows "Unknown Publisher" warning  
✅ **With signing:** Professional, trusted application appearance

### How to Code Sign

1. **Purchase certificate:**
   - DigiCert: https://www.digicert.com/code-signing
   - Sectigo: https://sectigo.com/ssl-certificates-tls/code-signing
   - Cost: ~$100-300/year

2. **Install certificate:**
   - Receive `.pfx` file and password
   - Install to Windows Certificate Store

3. **Sign executable:**
   ```bash
   # Sign TestBuddy.exe
   signtool sign /f certificate.pfx /p PASSWORD /t http://timestamp.digicert.com /fd SHA256 dist\TestBuddy.exe
   
   # Sign installer
   signtool sign /f certificate.pfx /p PASSWORD /t http://timestamp.digicert.com /fd SHA256 TestBuddy-Setup.exe
   ```

4. **Verify signature:**
   - Right-click executable → Properties → Digital Signatures
   - Should show your company name

---

## Build Configuration

### testbuddy.spec Overview

The PyInstaller spec file configures the build process:

```python
# Key configurations:
hiddenimports = [...]  # Explicitly include modules
excludes = [...]       # Exclude unnecessary modules
console = False        # GUI app (no console)
upx = True            # Compress with UPX
icon = 'icon.ico'     # Application icon
```

**Customization options:**

1. **Reduce size:** Add more modules to `excludes`
2. **Debug mode:** Set `console = True` to see error messages
3. **Multi-file mode:** Use COLLECT instead of single EXE
4. **Version info:** Create version resource file

### Reducing Executable Size

**Current size:** ~100-150 MB  
**Target size:** ~80-100 MB

**Optimization strategies:**

1. **Exclude unused modules:**
   ```python
   excludes = ['matplotlib', 'scipy', 'pandas', 'unittest', 'test']
   ```

2. **Enable UPX compression:**
   - Already enabled in spec: `upx=True`
   - Download UPX: https://upx.github.io/

3. **Multi-file distribution:**
   - Change to `--onedir` mode (app + folder of DLLs)
   - Smaller main executable but more files

4. **Remove debug info:**
   ```python
   strip = True  # Remove debug symbols
   ```

---

## Testing Checklist

### Pre-Distribution Testing

Test on **clean Windows VM** (no Python installed):

#### ✅ Installation Tests
- [ ] Installer runs without errors
- [ ] Installation progress shows correctly
- [ ] Shortcuts created (Desktop + Start Menu)
- [ ] Application appears in Add/Remove Programs
- [ ] Installation directory is `C:\Program Files\TestBuddy`

#### ✅ Functional Tests
- [ ] Application launches from shortcut
- [ ] No error messages on startup
- [ ] Can create new session
- [ ] Can edit session metadata
- [ ] Can capture screenshot (Snipping Tool launches)
- [ ] OCR processing works (requires Tesseract)
- [ ] Can save session
- [ ] Can load session from history
- [ ] Search/filter works
- [ ] Favorites system works
- [ ] Undo/Redo functional
- [ ] Export to PDF works
- [ ] Export to DOCX works
- [ ] Export to CSV, HTML, JSON, Markdown works
- [ ] Document Intelligence panel accessible
- [ ] No crash on exit

#### ✅ Uninstallation Tests
- [ ] Uninstaller runs from Start Menu
- [ ] Uninstaller runs from Add/Remove Programs
- [ ] All files removed
- [ ] Shortcuts removed
- [ ] Registry entries cleaned
- [ ] Application folder deleted

---

## Troubleshooting

### Build Issues

#### "Python not found"
**Solution:** Add Python to PATH:
```bash
# Check Python location
where python

# Add to PATH (System Properties → Environment Variables)
C:\Users\YourName\AppData\Local\Programs\Python\Python312
C:\Users\YourName\AppData\Local\Programs\Python\Python312\Scripts
```

#### "PyInstaller not found"
**Solution:**
```bash
pip install pyinstaller
```

#### "Failed to execute script"
**Solution:** Enable console mode to see errors:
```python
# In testbuddy.spec:
console = True  # Change from False
```

#### "Module not found" errors
**Solution:** Add missing module to `hiddenimports`:
```python
hiddenimports = [
    # ... existing imports ...
    'missing_module_name',
]
```

### Runtime Issues

#### "Tesseract not found"
**Error:** OCR fails with tesseract error

**Solution:**
1. Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Update path in `testbuddy.ini`:
   ```ini
   [ocr]
   tesseract_path = C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

#### "DLL load failed"
**Error:** Missing Windows DLL

**Solution:**
- Install Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe

#### "Access denied" during installation
**Error:** Installer fails with permission error

**Solution:**
- Right-click installer → "Run as Administrator"

---

## Distribution

### Release Checklist

Before distributing TestBuddy-Setup.exe:

1. ✅ **Test on clean Windows VM**
2. ✅ **Verify all features work**
3. ✅ **Check file size is reasonable** (~100-150 MB)
4. ✅ **Code sign executable** (optional but recommended)
5. ✅ **Create release notes**
6. ✅ **Update version number** in `.nsi` file
7. ✅ **Test uninstaller**
8. ✅ **Scan with antivirus** (VirusTotal.com)

### Upload to GitHub Releases

```bash
# Tag release
git tag -a v3.0.0 -m "Phase 3a: Native Windows Build"
git push origin v3.0.0

# Create GitHub Release
# 1. Go to: https://github.com/solaceking/Testbuddy/releases
# 2. Click "Create a new release"
# 3. Select tag: v3.0.0
# 4. Title: "TestBuddy v3.0.0 - Native Windows Build"
# 5. Upload: TestBuddy-Setup.exe
# 6. Write release notes (see template below)
```

### Release Notes Template

```markdown
## TestBuddy v3.0.0 - Native Windows Build

### 🎉 What's New
- **Native Windows Executable**: Standalone .exe installer
- **No Python Required**: Runs on any Windows 10/11 machine
- **Professional Installer**: NSIS-based setup wizard
- **Desktop & Start Menu Shortcuts**: Easy access

### 📦 Download
- **TestBuddy-Setup.exe** (100 MB) - Full installer

### 📋 Requirements
- Windows 10 or Windows 11 (64-bit)
- Tesseract OCR (download separately)

### 🔧 Installation
1. Download TestBuddy-Setup.exe
2. Run installer (may need administrator rights)
3. Follow setup wizard
4. Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
5. Launch TestBuddy from Start Menu or Desktop

### ✨ Features
- Session management (create, edit, delete, history)
- Multi-format export (PDF, DOCX, CSV, HTML, JSON, Markdown, TXT)
- Search and filter sessions
- Favorites system
- Undo/Redo support
- Document Intelligence (OCR, classification, field extraction)
- Rich text formatting toolbar

### 🐛 Bug Fixes
- None (first native Windows release)

### 📚 Documentation
- [User Guide](README_V2.md)
- [Build Guide](NATIVE_WINDOWS_BUILD.md)

### 🙏 Credits
- Built with PyQt6, Tesseract, and PyInstaller
```

---

## Advanced Topics

### Windows Dark Mode Support

Add dark mode detection in `app.py`:

```python
# In MainWindow.__init__():
if sys.platform == "win32":
    import winreg
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        if value == 0:
            # Apply dark theme
            self.apply_dark_theme()
    except:
        pass
```

### System Tray Integration

Add system tray icon for background operation:

```python
from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtGui import QIcon

# In MainWindow:
self.tray_icon = QSystemTrayIcon(QIcon("icon.ico"), self)
self.tray_icon.setToolTip("TestBuddy OCR Workbench")
self.tray_icon.activated.connect(self.tray_icon_activated)
self.tray_icon.show()
```

### Auto-Update System

Implement update checker:

```python
import requests

def check_for_updates():
    try:
        response = requests.get("https://api.github.com/repos/solaceking/Testbuddy/releases/latest")
        latest_version = response.json()["tag_name"]
        current_version = "v3.0.0"
        if latest_version > current_version:
            # Show update dialog
            pass
    except:
        pass
```

---

## File Structure

```
Testbuddy/
├── app.py                          # Main application
├── document_intelligence.py        # Phase 2c features
├── export.py                       # Export functionality
├── undo_redo.py                    # Undo/redo system
├── config.py                       # Configuration
├── history.py                      # Session management
│
├── testbuddy.spec                  # ✅ PyInstaller configuration
├── testbuddy_installer.nsi         # ✅ NSIS installer script
├── build_windows.bat               # ✅ Automated build script
├── build_windows.sh                # ✅ Cross-platform build
├── requirements.txt                # ✅ Updated with pyinstaller
├── LICENSE.txt                     # ✅ MIT License
├── icon.ico                        # ⚠️  Create manually
│
├── NATIVE_WINDOWS_BUILD.md         # ✅ This file
├── README_V2.md                    # User documentation
├── PHASE2C_COMPLETE.md             # Phase 2c documentation
│
└── dist/                           # Build output
    └── TestBuddy.exe               # ✅ Standalone executable
```

---

## Summary

✅ **What's Complete:**
- PyInstaller configuration (`testbuddy.spec`)
- NSIS installer script (`testbuddy_installer.nsi`)
- Automated build script (`build_windows.bat`)
- Cross-platform build script (`build_windows.sh`)
- Updated requirements.txt with pyinstaller
- MIT License (LICENSE.txt)
- Complete build documentation (this file)

⚠️ **What's Needed:**
- `icon.ico` file (create manually or use default)
- Test build on native Windows machine
- Code signing certificate (optional)

📦 **Deliverables:**
- `TestBuddy.exe` - Standalone executable
- `TestBuddy-Setup.exe` - Professional installer

---

## Next Steps

1. **Build on Windows:**
   ```bash
   git clone https://github.com/solaceking/Testbuddy.git
   cd Testbuddy
   build_windows.bat
   ```

2. **Test executable:**
   ```bash
   dist\TestBuddy.exe
   ```

3. **Create installer:**
   - Right-click `testbuddy_installer.nsi` → Compile NSIS Script

4. **Test installer:**
   - Run `TestBuddy-Setup.exe`
   - Verify all features work

5. **Distribute:**
   - Upload to GitHub Releases
   - Share download link

---

## Support

### Getting Help
- GitHub Issues: https://github.com/solaceking/Testbuddy/issues
- Documentation: `README_V2.md`
- Build Issues: Check "Troubleshooting" section above

### Reporting Bugs
When reporting build issues, include:
- Windows version (10/11)
- Python version (`python --version`)
- Build log output
- Error messages (if any)

---

**Build Date:** December 3, 2025  
**Phase:** 3a - Native Windows Packaging  
**Status:** Build System Complete ✅  
**Next Phase:** Testing & Distribution

---

*Happy building! TestBuddy is almost ready for widespread Windows distribution.* 🎉
