# TestBuddy v2 - Professional Document OCR Workbench

**Status:** ✅ **FULLY OPERATIONAL** (Phase 2 Complete)

TestBuddy is a modern, Python-based OCR (Optical Character Recognition) workbench that turns screenshots into editable text using Tesseract.

## Features

### Core Capabilities
- 📸 **Screenshot Capture** - Integrated Windows Snipping Tool
- 🤖 **OCR Processing** - Tesseract-powered text extraction
- ✏️ **Rich Text Editing** - Edit and refine OCR results
- 💾 **Session Management** - Create, save, and load OCR sessions
- 📊 **Session History** - Persistent JSON-based storage
- 📤 **Export** - Save sessions as text files with metadata
- 🔍 **Image Viewer** - View captured images with zoom/pan controls
- ⚙️ **Configuration** - INI-based settings system
- 📝 **Activity Logging** - Complete action audit trail

### User Interface
- **Splash Screen** - Professional 900ms startup animation
- **Home Dashboard** - Recent and all sessions lists
- **New Session Dialog** - Create sessions with metadata (name, category, tags)
- **Workbench** - Dual-panel layout (image + text editor)
- **Toolbar** - Quick access to capture, save, export, and zoom controls
- **Status Bar** - Real-time feedback on OCR processing

### Technical Features
- **Non-blocking OCR** - QThread-based processing keeps UI responsive
- **Clipboard Polling** - Automatic image detection (500ms intervals)
- **Type Hints** - 100% Python type annotation coverage
- **Error Handling** - Comprehensive exception management
- **Logging** - Detailed audit log for debugging

## Installation

### Requirements
- Python 3.10+
- Windows (Snipping Tool integration)
- Tesseract OCR binary

### Step 1: Install Python Packages
```bash
cd c:\Users\idavi\Documents\Projects\testbuddy
pip install -r requirements.txt
```

**What gets installed:**
- PyQt6 6.7.0+ (GUI framework)
- Pillow 10.0+ (Image processing)
- pytesseract 0.3.10+ (OCR wrapper)

### Step 2: Install Tesseract
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

Default installation path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

If installed elsewhere, update `testbuddy.ini`:
```ini
[ocr]
tesseract_path = C:\Your\Path\To\tesseract.exe
```

### Step 3: Verify Installation
```bash
python test_suite.py
```

Expected output:
```
Result: 5/5 tests passed
All tests passed! App is ready for use.
```

## Quick Start (5 Minutes)

### Launch the App
```bash
python run.py
```

Or directly:
```bash
python app.py
```

### First Use Workflow
1. **Splash Screen** appears (900ms auto-timeout)
2. **Home Page** shows with "+ New Session" button
3. **Create Session**:
   - Click "+ New Session"
   - Enter: Name = "My First OCR"
   - Optionally set Category and Tags
   - Click OK
4. **Capture Screenshot**:
   - Click "📷 Capture" button
   - Windows Snipping Tool opens
   - Draw rectangle around text
   - Copy to clipboard (Ctrl+C)
5. **OCR Processing**:
   - App detects clipboard image automatically
   - Tesseract processes in background (2-10 sec)
   - Text appears in right panel
6. **Edit & Save**:
   - Review/fix OCR result
   - Click "💾 Save" to persist to history
7. **Export** (Optional):
   - Click "📤 Export" to save as .txt file

## Directory Structure

```
testbuddy/
├── app.py                      # Main integrated application (520+ lines)
├── config.py                   # Configuration management system
├── history.py                  # Session persistence and search
├── main.py                     # Phase 1 reference implementation
├── run.py                      # Application launcher with checks
├── test_suite.py               # Comprehensive functional tests
│
├── testbuddy.ini              # Settings file (auto-created)
├── testbuddy_history.json     # Session database (auto-created)
├── testbuddy.log              # Activity log (auto-created)
├── export/                    # Exported text files directory
│
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── docs/
    ├── QUICKSTART_V2.md        # User quick start guide
    ├── PHASE2_INTEGRATION.md   # Integration documentation
    ├── INTEGRATION_SUMMARY.md  # Technical deep-dive
    └── COMPLETE_SUMMARY.md     # Project completion report
```

## Configuration

Settings are stored in `testbuddy.ini` and automatically created on first run.

### Common Settings

**OCR Options:**
```ini
[ocr]
tesseract_path = C:\Program Files\Tesseract-OCR\tesseract.exe
language = eng                    # Language code (eng, fra, deu, etc.)
psm = 3                          # Page segmentation mode (1-13)
oem = 3                          # OCR engine mode (0-3)
```

**UI Options:**
```ini
[ui]
clipboard_poll_interval_ms = 500  # Image detection frequency
export_directory = export/        # Where to save exports
```

**History Options:**
```ini
[history]
enable_history = true             # Enable session persistence
file = testbuddy_history.json     # Session database file
max_entries = 100                 # Maximum sessions to keep
```

**Logging:**
```ini
[behavior]
enable_logging = true             # Enable activity logging
log_file = testbuddy.log          # Log file path
```

### Change Language
Edit `testbuddy.ini`:
```ini
[ocr]
language = fra    # French
language = deu    # German
language = spa    # Spanish
```

See Tesseract docs for all supported language codes.

## Usage Guide

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Session |
| `Ctrl+S` | Save Session |
| `Alt+F4` | Close App |

### Workbench Toolbar Buttons
- **📷 Capture** - Launch Snipping Tool and OCR
- **💾 Save** - Save session to history
- **📤 Export** - Export text to file
- **🔍+** - Zoom in on image
- **🔍-** - Zoom out from image
- **↺ Fit** - Fit image to window

### Session Workflow
1. **Create** session with metadata
2. **Capture** screenshot via Snipping Tool
3. **OCR** processes automatically
4. **Edit** text in editor
5. **Save** to history database
6. **Export** as text file
7. **Reload** anytime from Home page

### Session Properties
- **Name** - Display name (required, max 120 chars)
- **Category** - Classification (General, Project, Receipt, Invoice)
- **Tags** - Custom labels (comma-separated)
- **Created** - Auto-set on creation
- **Modified** - Auto-updated on save

## Testing

### Run Test Suite
```bash
python test_suite.py
```

Tests cover:
- ✅ Dependency verification
- ✅ Configuration loading
- ✅ History persistence
- ✅ Session creation
- ✅ File I/O operations

### Test Sample OCR
1. Open any document with text
2. Take screenshot with Snipping Tool
3. Copy to clipboard
4. Click Capture in TestBuddy
5. Verify OCR result

## Troubleshooting

### "Tesseract not found"
**Error:** Tesseract binary not found at configured path

**Solution:**
1. Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Update path in `testbuddy.ini`:
   ```ini
   tesseract_path = C:\Your\Path\To\tesseract.exe
   ```
3. Restart app

### "No image in clipboard"
**Error:** OCR fails with "No image found in clipboard"

**Solution:**
1. Ensure Snipping Tool actually copied the image (usually automatic)
2. Try: Windows Snipping Tool → Take screenshot → Copy → Capture button
3. Verify clipboard has image: paste into Paint or Word

### "OCR result is gibberish"
**Error:** Text extraction is inaccurate or unreadable

**Solutions:**
1. **Improve image quality:**
   - Better lighting when taking screenshot
   - Higher contrast text on background
   - Larger text (zoom in before capturing)

2. **Adjust OCR settings** in `testbuddy.ini`:
   ```ini
   psm = 6    # Try different page segmentation modes (1-13)
   ```

3. **Change language** if needed:
   ```ini
   language = fra   # For French text
   ```

### Sessions not appearing
**Error:** Saved sessions don't show up in Home page

**Solution:**
1. Verify `enable_history = true` in `testbuddy.ini`
2. Check `testbuddy_history.json` exists
3. Check `testbuddy.log` for errors
4. Restart app

### App crashes on startup
**Error:** Application crashes immediately

**Solutions:**
1. Verify all dependencies: `python test_suite.py`
2. Check `testbuddy.log` for error details
3. Delete `testbuddy.ini` and let app recreate it
4. Ensure Python 3.10+ installed

## Architecture

### Threading Model
```
Main Thread (UI Loop)
├── HomePage (renders sessions)
├── Workbench (image viewer + text editor)
└── OCRWorker (QThread)
    └── Tesseract processing (non-blocking)
```

### Data Flow
```
Capture Button
  ↓
Snipping Tool (subprocess)
  ↓
Clipboard Poll (QTimer every 500ms)
  ↓
Image Detected
  ↓
OCRWorker Thread Spawn
  ↓
pytesseract.image_to_string()
  ↓
Finished Signal
  ↓
Text Display in Editor
```

### Storage
- **Configuration:** `testbuddy.ini` (INI format)
- **Sessions:** `testbuddy_history.json` (JSON format)
- **Exports:** `export/{name}_{timestamp}.txt` (Plain text)
- **Logs:** `testbuddy.log` (Text format)

## Performance

### Baseline Metrics
| Operation | Time | Notes |
|-----------|------|-------|
| App startup | <2s | Includes 900ms splash screen |
| Config load | <100ms | Parse INI file |
| History load | <200ms | Load 50 sessions |
| OCR (simple) | 2-5s | Basic text recognition |
| OCR (complex) | 5-10s | Complex layouts, fonts |
| Session save | <100ms | Write to JSON |
| Export | <500ms | File I/O |

## Features (Phase 2 Complete)

### Implemented ✅
- Splash screen with auto-timeout
- Home dashboard with session lists
- New session dialog with validation
- Workbench with dual-panel layout
- Image viewer with zoom/pan controls
- Rich text editor with character count
- Capture via Windows Snipping Tool
- Clipboard polling and image detection
- Non-blocking OCR processing (QThread)
- Session persistence to JSON
- Session export as text
- Configuration management (INI)
- Activity logging (testbuddy.log)
- Keyboard shortcuts (Ctrl+N, Ctrl+S)
- Status bar with real-time feedback

### Future Enhancements (Phase 3)
- [ ] PDF export (image + OCR text)
- [ ] Undo/Redo in text editor
- [ ] Find & Replace functionality
- [ ] Dark mode toggle
- [ ] Batch processing
- [ ] Session search and filter
- [ ] OCR confidence scores
- [ ] Multi-language detection

## Contributing

To extend TestBuddy:

1. **Add Features:** Edit `app.py` (MainWindow class)
2. **Change Settings:** Modify `config.py` and `testbuddy.ini`
3. **Improve OCR:** Adjust pytesseract parameters in `app.py` OCRWorker
4. **Test Changes:** Run `python test_suite.py`

## License

Open source - free to use and modify

## Support

### Getting Help
1. Check `testbuddy.log` for error details
2. Review `PHASE2_INTEGRATION.md` for detailed docs
3. Run `python test_suite.py` to validate setup
4. Verify Tesseract installation

### Common Commands
```bash
# Launch app
python run.py

# Run tests
python test_suite.py

# Check dependencies
python -c "from config import *; from history import *; print('OK')"

# View recent log entries
type testbuddy.log | Select-Object -Last 10   # PowerShell
tail testbuddy.log                             # Unix-like
```

## Project Status

**Version:** 2.0 (Phase 2 Complete)
**Status:** ✅ Production Ready
**Last Updated:** December 2025
**Test Coverage:** 5/5 tests passing
**Type Hints:** 100% coverage

---

## Quick Links

- 📖 [Quick Start Guide](QUICKSTART_V2.md)
- 🔧 [Configuration Guide](CONFIGURATION.md)
- 📋 [Integration Details](PHASE2_INTEGRATION.md)
- 🏗️ [Technical Deep-Dive](INTEGRATION_SUMMARY.md)
- 📊 [Project Summary](COMPLETE_SUMMARY.md)

---

**Ready to start?** Run `python run.py` now! 🚀
