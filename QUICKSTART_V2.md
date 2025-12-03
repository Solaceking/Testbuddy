# TestBuddy v2: Quick Start (Phase 2 Integrated)

## Installation (One-time)

```bash
# Navigate to project
cd c:\Users\idavi\Documents\Projects\testbuddy

# Install dependencies
pip install -r requirements.txt

# Verify Tesseract is installed
# Should be at: C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Launch App

```bash
python app.py
```

Or in VS Code: Open `app.py` → Press `F5`

---

## First-Time Usage (5 minutes)

### 1. Splash Screen (900ms)
App starts with splash screen showing "TestBuddy" logo.

### 2. Home Page
After splash, you see the home dashboard:
- **"+ New Session" button** at top
- **Recent Sessions** list (empty on first run)
- **All Sessions** list (empty on first run)

### 3. Create Your First Session
1. Click **"+ New Session"**
2. Dialog appears:
   - **Session name**: Type `"My First OCR"` (required)
   - **Category**: Select `General` (optional)
   - **Tags**: Leave blank or type `"test"` (optional)
3. Click **OK**

### 4. Workbench Opens
You now see the editor with two panels:
- **Left panel**: Image viewer (placeholder)
- **Right panel**: Text editor (empty)
- **Top toolbar**: Three buttons (Capture, Save, Export)
- **Status bar**: Shows "Session: My First OCR"

### 5. Capture Screenshot
1. Click **"📷 Capture"** button
2. Windows Snipping Tool opens
3. Draw a rectangle around any text (e.g., from this document)
4. Copy to clipboard (usually automatic or Ctrl+C)
5. App detects clipboard image → **OCR processing starts**

**Status updates:**
- "Launching Snipping Tool..."
- "Image found, processing OCR..."
- "OCR complete (XXX chars)"

Text appears in the right panel!

### 6. Edit & Save
1. Review the OCR'd text (fix typos if needed)
2. Click **"💾 Save"** button
3. Confirmation message: "Session 'My First OCR' saved successfully."
4. Session is now in `testbuddy_history.json`

### 7. Return Home
1. Menu: **View → Home**
2. You see **"Recent Sessions"** now shows your session
3. Double-click to re-open and edit

### 8. Export Session (Bonus)
1. From workbench: Click **"📤 Export"**
2. Text saves to `export/My First OCR_{timestamp}.txt`
3. You can open this file in Notepad or Word

---

## Common Tasks

### Create a New Session
`Ctrl+N` or Menu: File → New Session

### Save Current Session
`Ctrl+S` or Menu: File → Save (or button in workbench)

### Return to Home Page
Menu: View → Home

### Capture Screenshot
Click **"📷 Capture"** button in workbench toolbar

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Session |
| `Ctrl+S` | Save Session |
| `Alt+F4` | Close App |

---

## File Locations

**Config:**
- `testbuddy.ini` (settings for OCR, UI, history)

**Data:**
- `testbuddy_history.json` (all saved sessions)
- `export/` folder (exported text files)

**Logs:**
- `testbuddy.log` (activity log for debugging)

---

## Troubleshooting

### No OCR result after capture?
1. Check Windows Snipping Tool actually copied image to clipboard
2. Verify Tesseract is installed: `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. Check `testbuddy.log` for error messages

### Sessions don't appear after saving?
1. Close app and restart
2. Verify `testbuddy_history.json` file exists
3. Check `testbuddy.log` for errors

### Tesseract not found?
1. Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Or update `tesseract_path` in `testbuddy.ini` to your installation

### Need different language?
Edit `testbuddy.ini`:
```ini
[ocr]
language = fra  ; for French
```
Restart app.

---

## Next Steps

- **Refine OCR:** Try different languages, adjust PSM (page segmentation mode)
- **Bulk Export:** Select multiple sessions and export as PDF (coming soon)
- **Dark Mode:** Configure in preferences (coming soon)
- **Batch Process:** Process multiple images without manual steps (coming soon)

---

## Support

1. Check `testbuddy.log` for error messages
2. Review `PHASE2_INTEGRATION.md` for detailed usage
3. Check `README.md` for project overview

---

**You're all set!** 🚀

Start capturing screenshots, OCR them, edit, and save. Enjoy TestBuddy v2!
