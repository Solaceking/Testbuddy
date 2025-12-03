# TestBuddy Development Guide

## Project Architecture

```
TestBuddy (main.py)
    ├── Config Management (config.py)
    │   └── INI File ← Settings
    ├── History Management (history.py)
    │   └── JSON File ← OCR Sessions
    └── PyQt6 GUI (main.py)
        ├── OCRWorker Thread (non-blocking)
        │   └── Tesseract OCR
        └── UI Components
            ├── Screenshot Control
            ├── Text Editor
            ├── Activity Log
            └── Buttons & Shortcuts
```

## Code Organization

### `config.py` — Configuration System
- **Config dataclass**: All settings with type hints
- **ConfigManager**: Load/save INI files
- Features:
  - Type-safe access to settings
  - Default values
  - Error handling for missing/invalid values
  - INI persistence

### `history.py` — Session Persistence
- **HistoryEntry dataclass**: Single OCR result
- **HistoryManager**: JSON-based storage
- Features:
  - Add, search, delete entries
  - Full-text search
  - Statistics generation
  - Auto-save

### `main.py` — Main Application
- **OCRWorker**: QThread for non-blocking OCR
- **SnapOCRApp**: Main PyQt6 window
- Features:
  - Screenshot integration
  - Clipboard polling
  - UI rendering
  - Event handling
  - Logging

## Type Hints Usage

All functions are fully type-hinted:

```python
def process_image(self, image: Image.Image, language: str) -> str:
    """Process image and extract text."""
    pass

def add_entry(self, text: str, language: str = "eng", tags: Optional[List[str]] = None) -> None:
    """Add OCR result to history."""
    pass
```

**Benefits:**
- IDE autocomplete ✓
- Static type checking with mypy
- Self-documenting code
- Early error detection

## Running & Testing

### Basic Execution
```powershell
python main.py
```

### Check for Syntax Errors
```powershell
python -m py_compile main.py config.py history.py
```

### Type Checking (Optional, requires mypy)
```powershell
pip install mypy
mypy main.py config.py history.py
```

### View Activity Log
```powershell
type testbuddy_debug.log
```

## Phase 2: Next Enhancements

### 1. Multi-Language Selector (Easy, 1-2 hours)

Add UI dropdown for language selection:

```python
# In _build_ui():
self.language_combo = QComboBox(self)
self.language_combo.addItems(["English (eng)", "French (fra)", "German (deu)", ...])
self.language_combo.currentTextChanged.connect(self.on_language_changed)

def on_language_changed(self, text: str) -> None:
    code = text.split("(")[1].rstrip(")")
    config.ocr_language = code
    config_manager.save()
```

### 2. Image Preview (Medium, 2-3 hours)

Display captured screenshot before OCR:

```python
# In history.py or new preview.py:
@dataclass
class ImagePreview:
    image: Image.Image
    timestamp: str
    dimensions: tuple
    file_size: int

# In main.py:
def show_image_preview(self, img: Image.Image) -> None:
    preview_dialog = QDialog(self)
    layout = QVBoxLayout()
    label = QLabel()
    label.setPixmap(QPixmap.fromImage(img))
    layout.addWidget(label)
    preview_dialog.exec()
```

### 3. Undo/Redo (Medium, 2-3 hours)

Use QTextEdit's built-in undo/redo:

```python
# Already supported in QTextEdit!
# Just enable:
self.text_area = QTextEdit(left)
self.text_area.setReadOnly(False)
self.text_area.setUndoRedoEnabled(True)

# Add buttons:
self.btn_undo = QPushButton("Undo", left)
self.btn_undo.setShortcut("Ctrl+Z")
self.btn_undo.clicked.connect(self.text_area.undo)

self.btn_redo = QPushButton("Redo", left)
self.btn_redo.setShortcut("Ctrl+Y")
self.btn_redo.clicked.connect(self.text_area.redo)
```

### 4. Dark Mode (Hard, 4-5 hours)

Create theme system:

```python
# New file: themes.py
class Theme:
    name: str
    background: str
    text: str
    button: str
    
LIGHT = Theme(name="light", background="#ffffff", text="#000000", button="#007bff")
DARK = Theme(name="dark", background="#1e1e1e", text="#ffffff", button="#0d6efd")

def apply_theme(app: QApplication, theme: Theme) -> None:
    stylesheet = f"""
        QMainWindow {{ background-color: {theme.background}; }}
        QTextEdit {{ background-color: {theme.background}; color: {theme.text}; }}
    """
    app.setStyleSheet(stylesheet)
```

## Code Quality Standards

### Type Hints (Mandatory)
```python
# ✓ Good
def function(param: str, count: int = 5) -> Optional[str]:
    pass

# ✗ Bad
def function(param, count=5):
    pass
```

### Docstrings (Required for classes/public methods)
```python
class MyClass:
    """Short description.
    
    Longer explanation of what this class does and how to use it.
    """
    
    def public_method(self) -> None:
        """Do something important."""
        pass
```

### Error Handling
```python
# ✓ Good - Specific exceptions
try:
    result = pytesseract.image_to_string(img)
except FileNotFoundError:
    self._log("ERROR", "Tesseract not found")
except Exception as e:
    self._log("ERROR", f"OCR failed: {e}")

# ✗ Bad - Bare except
try:
    result = pytesseract.image_to_string(img)
except:
    pass
```

### Logging Standards
```python
# ✓ Good - Structured logging
self._log("INFO", "OCR started", f"language={config.ocr_language}")
self._log("ERROR", "Export failed", str(exception))

# ✗ Bad - Vague logging
print("Started")
print("Error!")
```

## Adding New Features

### Template for New Feature

1. **Define config options** (if needed)
```python
# In config.py, add to Config dataclass:
new_feature_enabled: bool = True
```

2. **Create feature module** (if complex)
```python
# new_feature.py
class NewFeature:
    def __init__(self, config: Config):
        self.config = config
    
    def process(self, data: str) -> str:
        """Process data."""
        return data
```

3. **Integrate into main.py**
```python
from new_feature import NewFeature

# In SnapOCRApp.__init__():
self.feature = NewFeature(config)

# In action method:
self.feature.process(self._last_text)
```

4. **Add UI controls** (if user-facing)
```python
# In _build_ui():
self.btn_feature = QPushButton("New Feature", self)
self.btn_feature.clicked.connect(self.on_feature_clicked)

def on_feature_clicked(self) -> None:
    result = self.feature.process(self._last_text)
    self._log("INFO", "Feature executed")
```

5. **Test & document**
```python
# Write docstrings
# Update README.md
# Add config explanation to CONFIGURATION.md
```

## Future Architecture Improvements

### Proposed: Plugin System
```python
class Plugin(ABC):
    @abstractmethod
    def process(self, text: str) -> str:
        pass

class SpellChecker(Plugin):
    def process(self, text: str) -> str:
        # Correct spelling
        return corrected_text
```

### Proposed: Settings GUI
```python
class SettingsDialog(QDialog):
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        # Generate UI from Config dataclass
        # Save changes back
```

### Proposed: Advanced History Search
```python
# Currently: Simple text search
# Future: 
#   - Date range filtering
#   - Tag-based filtering
#   - Duplicate detection
#   - Export/import sessions
```

## Testing Checklist Before Release

- [ ] Test with simple text images
- [ ] Test with complex layouts (tables, columns)
- [ ] Test with multiple languages
- [ ] Test history save/load
- [ ] Test settings persistence
- [ ] Check log file is created
- [ ] Verify no crashes on edge cases
- [ ] Test keyboard shortcuts
- [ ] Test with non-admin user
- [ ] Check memory usage (< 500MB)

## Performance Optimization Tips

1. **Reduce polling interval** for faster response (tradeoff: CPU)
2. **Cache recent OCR results** to avoid re-processing
3. **Lazy-load language data** (only load when needed)
4. **Use threading** for any blocking operation (already done for OCR)
5. **Limit history size** to prevent JSON bloat

## Common Pitfalls & Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| Slow OCR | Complex image | Crop/simplify before OCR |
| Memory leak | History grows | Implement size limits |
| UI freezes | Blocking operation | Move to QThread |
| Lost settings | File not saved | Call config_manager.save() |
| Empty history | JSON corrupted | Delete and restart |

---

## Resources

- **PyQt6 Docs**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **Tesseract OCR**: https://github.com/UB-Mannheim/tesseract/wiki
- **Python Type Hints**: https://docs.python.org/3/library/typing.html
- **Python Logging**: https://docs.python.org/3/howto/logging.html

---

**Ready to contribute?** Start with Phase 2 items above!  
**Questions?** Check `testbuddy_debug.log` for runtime errors.

**Version**: 1.0.0  
**Last Updated**: December 2025
