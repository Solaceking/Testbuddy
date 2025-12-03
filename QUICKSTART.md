# TestBuddy Quick Start Guide

Get up and running in 5 minutes.

## Installation (5 minutes)

### Step 1: Install Tesseract OCR
Download and run the Windows installer:
https://github.com/UB-Mannheim/tesseract/wiki

Default installation path is fine: `C:\Program Files\Tesseract-OCR`

### Step 2: Install Python Dependencies
```powershell
cd c:\Users\idavi\Documents\Projects\testbuddy
pip install -r requirements.txt
```

### Step 3: Launch TestBuddy
```powershell
python main.py
```

**First Run**: App creates `testbuddy.ini` with default settings.

---

## 5-Minute Workflow

1. **Open TestBuddy** (app stays on top)
2. **Press Ctrl+Shift+S** → Windows Snipping Tool opens
3. **Capture text** → Snip the area with text
4. **Wait 1-3 seconds** → OCR processes automatically
5. **Ctrl+C** → Copy text or click "COPY TEXT" button
6. **Done!** → Text now in your clipboard

---

## Key Features Overview

| Feature | Shortcut | How to Use |
|---------|----------|-----------|
| Capture | Ctrl+Shift+S | Launch screenshot tool |
| Copy | Ctrl+C | Copy extracted text |
| History | Button | View last 10 OCR sessions |
| Export | Button | Save text to file |
| Help | Button | View keyboard shortcuts |

---

## First-Time Customization

### Change OCR Language
Open `testbuddy.ini` and edit:
```ini
[tesseract]
language = fra    # Change to French
```

Save and restart app. Common codes: `eng` (English), `fra` (French), `deu` (German), `spa` (Spanish), `jpn` (Japanese).

See `CONFIGURATION.md` for complete language list.

### Auto-Copy Text
Edit `testbuddy.ini`:
```ini
[behavior]
auto_copy_on_ocr = True
```

Now OCR results auto-copy to clipboard (no manual copy needed).

### Disable History
Edit `testbuddy.ini`:
```ini
[history]
enable_history = False
```

This saves memory and doesn't track past OCR sessions.

---

## Files Generated

After first run, these files appear:

| File | Purpose | Safe to Delete? |
|------|---------|-----------------|
| `testbuddy.ini` | Settings | No (regenerated with defaults) |
| `testbuddy_history.json` | OCR history | Yes (history lost) |
| `testbuddy_debug.log` | Activity log | Yes (diagnostics lost) |
| `exports/` | Exported sessions | Yes (old exports lost) |

---

## Troubleshooting

### "Tesseract not found" Error
1. Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (default path is fine)
3. Restart TestBuddy

### OCR gives wrong text
Try different capture mode:
1. Edit `testbuddy.ini`:
```ini
[tesseract]
psm = 3    # Try 3, 6, 11 (currently 6)
```

2. Restart and try again

### App is slow or unresponsive
1. Close other applications
2. Try simpler screenshot (less text)
3. Check `testbuddy_debug.log` for errors

### Want to reset all settings
```powershell
del testbuddy.ini
del testbuddy_history.json
del testbuddy_debug.log
python main.py
```

---

## What's Next?

- ✅ **Phase 1 Complete**: Config, keyboard shortcuts, history, type hints
- 🎯 **Phase 2 (Planned)**: Image preview, multi-language UI, undo/redo, dark mode
- 🚀 **Phase 3 (Planned)**: Batch processing, CSV/JSON export, corrections
- 📦 **Phase 4 (Planned)**: Packaging, Windows installer, auto-updater

---

## System Requirements

- **Windows 10/11** (not Mac/Linux)
- **Python 3.8+** (`python --version` to check)
- **Tesseract OCR** (installed separately)
- **RAM**: 256MB minimum, 512MB recommended
- **Disk**: 50MB for installation + 100MB for language data

---

## Need Help?

1. **Check Activity Log**: Right panel shows what app is doing
2. **Review `testbuddy_debug.log`**: Detailed error messages
3. **Read `CONFIGURATION.md`**: All settings explained
4. **See `README.md`**: Full feature documentation

---

**Ready to extract text?** Press `Ctrl+Shift+S` and take a screenshot! 📸

**Version**: 1.0.0  
**Last Updated**: December 2025
