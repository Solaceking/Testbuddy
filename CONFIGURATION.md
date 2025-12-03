# TestBuddy Configuration Guide

## Overview

TestBuddy stores all settings in `testbuddy.ini` (auto-generated on first run). This guide explains each configuration option.

## File Format

Standard INI format with sections:

```ini
[section_name]
setting_name = value
```

## Sections & Options

### [tesseract] — OCR Engine Settings

#### `path` (string)
Location of Tesseract-OCR executable.

- **Default**: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- **Example**: `C:\Custom\Path\tesseract.exe`
- **Note**: Required for OCR to work

#### `language` (string)
OCR language(s) to recognize. Use ISO 639-3 codes.

- **Default**: `eng` (English)
- **Single**: `fra` (French only)
- **Multiple**: `eng+fra+deu` (English + French + German)
- **All**: `osd` (auto-detect)
- **Common Codes**:
  - `eng` — English
  - `fra` — French
  - `deu` — German
  - `spa` — Spanish
  - `jpn` — Japanese
  - `chi_sim` — Simplified Chinese
  - `chi_tra` — Traditional Chinese
  - `ara` — Arabic
  - Full list: https://github.com/UB-Mannheim/tesseract/wiki/Data-Files

#### `psm` (integer, 0-13)
Page Segmentation Mode — how Tesseract analyzes page layout.

- **0**: OSD only (Orientation and Script Detection)
- **1**: Auto with OSD
- **3**: Fully automatic (DEFAULT)
- **6**: Assume single uniform block of text (RECOMMENDED)
- **11**: Sparse text (good for receipts/forms)
- **13**: Raw line (treat as single line)
- **Test different values** if results are poor

#### `oem` (integer, 0-3)
OCR Engine Mode — Tesseract's processing engine.

- **0**: Legacy engine only
- **1**: Neural net LSTM only
- **2**: Legacy + LSTM (Default)
- **3**: LSTM + Legacy (BEST - uses both)**
- **Note**: Requires LSTM training data for languages

### [ui] — User Interface Settings

#### `window_width` (integer)
Main window width in pixels.

- **Default**: `900`
- **Minimum**: `700`
- **Recommended**: `900-1200`

#### `window_height` (integer)
Main window height in pixels.

- **Default**: `600`
- **Minimum**: `500`
- **Recommended**: `600-800`

#### `window_always_on_top` (boolean)
Keep window on top of all other windows.

- **Default**: `True`
- **Options**: `True`, `False`
- **Useful for**: Multitasking, quick captures

#### `theme` (string)
UI color theme.

- **Default**: `light`
- **Options**: `light` (only option currently)
- **Future**: `dark` (planned)

#### `splitter_ratio` (integer)
Left panel width (pixels) when window split between text & log.

- **Default**: `600`
- **Range**: `300-1000`
- **Note**: Right panel gets remaining space

### [behavior] — Application Behavior

#### `clipboard_poll_interval_ms` (integer)
How often (milliseconds) to check clipboard for new images.

- **Default**: `500` (half second)
- **Lower** (e.g., 200): More responsive, higher CPU
- **Higher** (e.g., 1000): Less responsive, lower CPU
- **Recommended**: `500`

#### `log_buffer_size` (integer)
How many activity log lines to keep in memory.

- **Default**: `100`
- **Range**: `50-500`
- **Note**: Older entries still in `testbuddy_debug.log`

#### `auto_copy_on_ocr` (boolean)
Automatically copy extracted text to clipboard.

- **Default**: `False`
- **Options**: `True`, `False`
- **When True**: No need to click COPY TEXT button

### [history] — Session History

#### `enable_history` (boolean)
Save all OCR results to history file.

- **Default**: `True`
- **Options**: `True`, `False`
- **When False**: History button disabled, no storage overhead

#### `max_entries` (integer)
Maximum OCR sessions to keep in history.

- **Default**: `100`
- **Range**: `10-1000`
- **Note**: Oldest entries deleted when limit reached

#### `file` (string)
Filename for history data.

- **Default**: `testbuddy_history.json`
- **Format**: JSON (human-readable)
- **Location**: Same directory as main.py

### [export] — Session Export

#### `format` (string)
Default export file format.

- **Default**: `txt`
- **Current Options**: `txt`
- **Future**: `csv`, `json`, `pdf`

#### `directory` (string)
Folder for exported sessions.

- **Default**: `exports`
- **Example**: `C:\Users\you\Documents\OCR Exports`
- **Note**: Auto-created if missing

### [logging] — Debug Logging

#### `file` (string)
Activity log filename.

- **Default**: `testbuddy_debug.log`
- **Location**: Same directory as main.py
- **Format**: Plain text, timestamped

#### `debug_mode` (boolean)
Enable verbose logging (planned).

- **Default**: `False`
- **Options**: `True`, `False`
- **Note**: Currently logged regardless

## Example Configurations

### Minimal (English Only)
```ini
[tesseract]
path = C:\Program Files\Tesseract-OCR\tesseract.exe
language = eng
psm = 6
oem = 3

[history]
enable_history = False
```

### Multilingual (English + French + German)
```ini
[tesseract]
path = C:\Program Files\Tesseract-OCR\tesseract.exe
language = eng+fra+deu
psm = 6
oem = 3
```

### Performance-Optimized (Low CPU)
```ini
[behavior]
clipboard_poll_interval_ms = 1000
log_buffer_size = 50

[history]
enable_history = True
max_entries = 50
```

### Production (Full Featured)
```ini
[tesseract]
path = C:\Program Files\Tesseract-OCR\tesseract.exe
language = eng
psm = 6
oem = 3

[ui]
window_width = 1200
window_height = 800
window_always_on_top = False

[behavior]
auto_copy_on_ocr = True

[history]
enable_history = True
max_entries = 200

[export]
directory = C:\Users\you\Documents\OCR Exports

[logging]
debug_mode = True
```

## Troubleshooting Configuration

### Settings Not Loading
1. Check INI file syntax (colons not equals signs)
2. Verify section names in brackets
3. Look for typos in option names
4. Delete `testbuddy.ini` and restart to regenerate

### Changes Not Applied
1. **Configuration is loaded on startup** — Restart app
2. Check `testbuddy_debug.log` for load errors
3. Verify you edited correct file (check path)

### Invalid Values
```
Error: invalid literal for int() with base 10: 'invalid'
```

Ensure numeric fields contain only numbers:
```ini
window_width = 900        ✓ Correct
window_width = "900"      ✗ Wrong (remove quotes)
window_width = nine       ✗ Wrong (use numbers)
```

Boolean values must be capitalized:
```ini
enable_history = True     ✓ Correct
enable_history = true     ✗ Wrong (case-sensitive)
enable_history = 1        ✗ Wrong (use True/False)
```

## Advanced: Programmatic Access

Access config in Python:

```python
from config import ConfigManager

config_manager = ConfigManager()
config = config_manager.config

# Read
language = config.ocr_language
print(f"Using language: {language}")

# Modify
config.window_width = 1024
config.auto_copy_on_ocr = True

# Save
config_manager.save()
```

## Reset to Defaults

1. Delete `testbuddy.ini`
2. Restart application
3. New default config auto-generated

## Performance Tips

| Goal | Changes |
|------|---------|
| Faster Screenshot Response | Decrease `clipboard_poll_interval_ms` |
| Lower Memory Use | Reduce `log_buffer_size`, disable history |
| Better OCR Accuracy | Adjust `psm` (try 3, 6, 11) |
| Support More Languages | Add codes to `language` field |

---

**Last Updated**: December 2025  
**Applies To**: TestBuddy v1.0.0+
