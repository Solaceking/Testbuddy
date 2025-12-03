# TestBuddy v2: Phase 2 Integration Guide

## Overview

`app.py` is the fully integrated TestBuddy application combining Phase 1 backend (config, history, OCR) with a professional Phase 2 UI:

- **SplashScreen**: 900ms auto-timeout on startup
- **HomePage**: Dashboard with "+ New Session" button and session lists (recent + all)
- **NewSessionDialog**: Create session with name, category (General/Project/Receipt/Invoice), and tags
- **Workbench**: Dual-panel editor with image viewer + rich text editor
- **Integration Points**: 
  - ConfigManager (settings from testbuddy.ini)
  - HistoryManager (persistence to testbuddy_history.json)
  - OCRWorker thread (async Tesseract OCR from clipboard)

---

## Key Features

### 1. New Session Workflow
```
Home Page → "+ New Session" → Name/Category/Tags Dialog → Workbench
```
- Validates session name (required, max 120 chars)
- Assigns unique session ID (UUID)
- Switches to workbench for capture + editing

### 2. Capture → OCR Flow
```
Workbench → "📷 Capture" → Launches Snipping Tool → Polls clipboard → OCRWorker → Result in editor
```
- Launches Windows Snipping Tool (`explorer.exe ms-screenclip:`)
- Polls clipboard every 500ms for image (configurable via `clipboard_poll_interval_ms`)
- Runs Tesseract in background thread (non-blocking)
- Displays OCR result in text editor

### 3. Session Persistence
```
Workbench → "💾 Save" → HistoryEntry added to JSON → Home page updated
```
- Saves full OCR text to `testbuddy_history.json`
- Tags = session name for easy lookup
- Displays confirmation message
- Home page lists are refreshed on navigation

### 4. Session Loading
```
Home Page → Double-click session → Workbench with text loaded
```
- Click recent session (top 5) or all sessions list
- Text loaded into editor for review/export

### 5. Export Session
```
Workbench → "📤 Export" → Text saved to export directory
```
- Saves as `{session_name}_{timestamp}.txt`
- Default directory: `export/` (configurable via `testbuddy.ini`)
- Confirms export location

---

## Configuration

All settings are in `testbuddy.ini` (managed by `ConfigManager`):

### Key Settings for Phase 2

**OCR**
- `ocr_language`: Language code for Tesseract (default: `eng`)
- `ocr_psm`: Page segmentation mode (default: `3`)
- `ocr_oem`: OCR engine mode (default: `3`)

**UI**
- `clipboard_poll_interval_ms`: Poll frequency for clipboard images (default: `500`)
- `export_directory`: Where to save exported sessions (default: `export/`)

**History**
- `enable_history`: Enable session persistence (default: `true`)
- `history_file`: Path to JSON history file (default: `testbuddy_history.json`)
- `history_max_entries`: Max sessions to keep (default: `100`)

**Behavior**
- `enable_logging`: Log all actions (default: `true`)
- `log_file`: Log output file (default: `testbuddy.log`)

---

## Architecture

### Module Organization
```
testbuddy/
├── app.py                    # NEW: Main integrated app (Phase 2 UI + backend)
├── config.py                 # Phase 1: Configuration management
├── history.py                # Phase 1: Session persistence
├── main.py                   # Phase 1: Original app (OCRWorker, clipboard polling)
├── testbuddy.ini            # Settings file
├── testbuddy_history.json   # Session database
└── testbuddy.log            # Activity log
```

### Class Hierarchy
```
app.py:
├── OCRWorker(QObject)              # Thread-safe image processing
├── SplashScreen(QWidget)           # Auto-timeout splash (900ms)
├── NewSessionDialog(QDialog)       # Session creation form
├── HomePage(QWidget)               # Dashboard + session lists
├── Workbench(QWidget)              # Image viewer + rich text editor
└── MainWindow(QMainWindow)         # Main window + stacked pages

config.py:
├── Config                          # Dataclass (20+ settings)
└── ConfigManager                   # Load/save INI

history.py:
├── HistoryEntry                    # Dataclass (timestamp, text, tags, etc.)
└── HistoryManager                  # CRUD + search + JSON persistence
```

---

## Running the App

### From Command Line
```bash
cd c:\Users\idavi\Documents\Projects\testbuddy
python app.py
```

### From IDE
- Open `app.py` in VS Code
- Press `F5` to run with debugger
- Or: `Ctrl+Shift+D` → Python → Current file

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Session |
| `Ctrl+S` | Save Session |
| Menu: File → Exit | Quit app |
| Menu: View → Home | Return to home page |

---

## Workflow: End-to-End Example

1. **Launch App**
   - Splash screen shows for 900ms
   - Home page appears with recent/all sessions

2. **Create New Session**
   - Click "+ New Session"
   - Enter: Name = "Report 001", Category = "Project", Tags = "urgent, finance"
   - Click OK → Workbench opens

3. **Capture Image**
   - Click "📷 Capture" button
   - Windows Snipping Tool opens
   - Draw selection around text in image
   - Copy to clipboard
   - App detects image → Runs Tesseract → Results in editor (5-10 sec)

4. **Edit & Save**
   - Review OCR text, fix any errors
   - Click "💾 Save"
   - Session saved to `testbuddy_history.json`
   - Confirmation dialog appears

5. **Return to Home**
   - Menu: View → Home
   - New session appears in "Recent Sessions" list
   - Double-click to re-open and edit

6. **Export Session**
   - From workbench: Click "📤 Export"
   - Text saved to `export/Report 001_20250106_143052.txt`
   - Confirmation dialog

---

## Status Messages in Workbench

| Message | Meaning |
|---------|---------|
| "Ready" | Waiting for action |
| "Launching Snipping Tool..." | Opening Windows snipping tool |
| "Image found, processing OCR..." | Tesseract running |
| "OCR complete (X chars)" | Success! Text in editor |
| "OCR failed" | Error occurred (see log) |
| "Session saved" | Save completed |
| "Exported: {filename}" | Export successful |

---

## Logging

All actions are logged to `testbuddy.log`:

```
[2025-01-06 14:30:45] [INFO] TestBuddy v2 started
[2025-01-06 14:31:02] [INFO] New session created | name=Report 001
[2025-01-06 14:31:15] [INFO] Capture initiated
[2025-01-06 14:31:20] [INFO] OCR finished | chars=324
[2025-01-06 14:31:25] [INFO] Session saved | name=Report 001, chars=324
[2025-01-06 14:31:30] [INFO] Session exported | file=export/Report 001_20250106_143130.txt
```

---

## Troubleshooting

### "No image found in clipboard"
- Ensure you copied image to clipboard via Snipping Tool
- Verify clipboard contains image (not text)

### "OCR failed"
- Check tesseract.exe path in `testbuddy.ini`
- Verify Tesseract language pack is installed for chosen language
- See `testbuddy.log` for detailed error

### Sessions not appearing in Home
- Check if `enable_history = true` in `testbuddy.ini`
- Verify `testbuddy_history.json` exists and is valid JSON
- Check `testbuddy.log` for load errors

### App crashes on startup
- Ensure all requirements installed: `pip install -r requirements.txt`
- Verify Python 3.10+ (PyQt6 requirement)
- Check that config/history files are readable

---

## Next Steps (Phase 3)

Planned improvements:

1. **Image Viewer Enhancements**
   - Zoom in/out controls
   - Pan/scroll for large images
   - OCR bounding boxes overlay

2. **Rich Text Editor Features**
   - Undo/Redo (Ctrl+Z / Ctrl+Y)
   - Find & Replace (Ctrl+H)
   - Text formatting (bold, italic, monospace)

3. **Multi-Format Export**
   - PDF with image + OCR text
   - Word (.docx) with formatting
   - Markdown with metadata

4. **Batch Processing**
   - Process multiple images in sequence
   - Export all sessions as PDF/ZIP

5. **UI Polish**
   - Dark mode toggle
   - Custom color schemes
   - Toolbar icon sets

6. **Advanced OCR**
   - Tesseract confidence scores
   - Language auto-detection
   - Handwriting recognition

---

## Support

For issues or questions:
1. Check `testbuddy.log` for error messages
2. Review configuration in `testbuddy.ini`
3. Ensure dependencies installed: `pip install -r requirements.txt`
4. Verify Tesseract binary at `C:\Program Files\Tesseract-OCR\tesseract.exe`
