import sys
import os
import time
import traceback
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QSplitter, QMessageBox
)

from config import ConfigManager
from history import HistoryManager

# Dependencies: Pillow, pytesseract, pyperclip
try:
    from PIL import ImageGrab, Image
except Exception:
    ImageGrab = None
    Image = None
try:
    import pytesseract
except Exception:
    pytesseract = None
try:
    import pyperclip
except Exception:
    pyperclip = None


# Global config and history managers
config_manager: ConfigManager = ConfigManager()
config = config_manager.config
history_manager: HistoryManager = HistoryManager(
    config.history_file,
    config.history_max_entries
)


# Logging utilities
def safe_write_log(line: str) -> None:
    try:
        with open(config.log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fmt_log(level: str, message: str, details: Optional[str] = None) -> str:
    base = f"[{now_ts()}] [{level}] {message}"
    if details:
        base += f" | {details}"
    return base


# -----------------------------
# OCR worker (runs in background thread)
# -----------------------------
class OCRWorker(QObject):
    finished = pyqtSignal(str, str)  # (text, error)

    def __init__(self, parent=None):
        super().__init__(parent)

    def process_image_from_clipboard(self):
        start = time.time()
        try:
            # Validate dependencies
            if ImageGrab is None or Image is None:
                raise RuntimeError("Pillow (ImageGrab) is not available.")
            if pytesseract is None:
                raise RuntimeError("pytesseract is not available.")

            # Grab image from clipboard
            img = ImageGrab.grabclipboard()
            if img is None:
                raise RuntimeError("No image found in clipboard.")

            # Ensure proper mode and grayscale
            if img.mode != "RGB":
                img = img.convert("RGB")
            img_gray = img.convert("L")

            # Use configured OCR parameters
            ocr_config = f"--psm {config.ocr_psm} --oem {config.ocr_oem}"
            text = pytesseract.image_to_string(
                img_gray,
                lang=config.ocr_language,
                config=ocr_config
            )

            duration = round((time.time() - start) * 1000)
            self.finished.emit(text, "")
        except Exception as e:
            tb = traceback.format_exc()
            self.finished.emit("", f"{str(e)}\n{tb}")


# -----------------------------
# Main application
# -----------------------------
class SnapOCRApp(QMainWindow):
    POLL_INTERVAL_MS: int = 500  # Clipboard polling interval

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TestBuddy - Screenshot to Text Converter")
        self.setMinimumSize(700, 500)
        self.resize(config.window_width, config.window_height)
        
        window_flags = Qt.WindowType.WindowStaysOnTopHint if config.window_always_on_top else Qt.WindowType.Window
        self.setWindowFlags(window_flags)

        # Internal state
        self._polling: bool = False
        self._last_text: str = ""
        self._log_buffer: list[str] = []
        self.thread: Optional[QThread] = None
        self.worker: Optional[OCRWorker] = None

        # Build UI
        self._build_ui()

        # Platform validation
        self._validate_platform()

        # Initial status
        self._log("INFO", "Application started", f"Platform: {platform.platform()}")

    # ------------- UI construction -------------
    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Top toolbar
        toolbar_layout = QHBoxLayout()
        self.btn_help = QPushButton("Help", self)
        self.btn_help.clicked.connect(self.show_help)
        self.btn_help.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)

        self.btn_export = QPushButton("Export Session", self)
        self.btn_export.clicked.connect(self.export_session)
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)

        self.btn_history = QPushButton("History", self)
        self.btn_history.clicked.connect(self.show_history)
        self.btn_history.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)

        toolbar_layout.addWidget(self.btn_help)
        toolbar_layout.addWidget(self.btn_export)
        toolbar_layout.addWidget(self.btn_history)
        toolbar_layout.addStretch()

        main_layout.addLayout(toolbar_layout)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        main_layout.addWidget(splitter)

        # Left panel (Text area and buttons)
        left = QWidget(self)
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(10)

        # Top buttons
        top_buttons = QHBoxLayout()
        self.btn_copy = QPushButton("COPY TEXT", left)
        self.btn_copy.clicked.connect(self.copy_text)
        self.btn_copy.setShortcut("Ctrl+C")
        self.btn_copy.setEnabled(False)
        self.btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }
        """)

        top_buttons.addStretch()
        top_buttons.addWidget(self.btn_copy)
        top_buttons.addStretch()

        # Main text area
        self.text_area = QTextEdit(left)
        self.text_area.setReadOnly(False)

        # Bottom capture button
        bottom_layout = QHBoxLayout()
        self.btn_screenshot = QPushButton("📷", left)
        self.btn_screenshot.clicked.connect(self.take_screenshot)
        self.btn_screenshot.setShortcut("Ctrl+Shift+S")
        self.btn_screenshot.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border-radius: 50px;
                padding: 20px;
                width: 80px;
                height: 80px;
                font-size: 24px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0a84e1;
            }
            QPushButton:pressed {
                background-color: #0056b3;
            }
        """)

        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_screenshot)
        bottom_layout.addStretch()

        left_layout.addLayout(top_buttons)
        left_layout.addWidget(self.text_area)
        left_layout.addLayout(bottom_layout)

        # Right panel (Debug console)
        right = QWidget(self)
        right_layout = QVBoxLayout(right)
        right_layout.setSpacing(8)

        debug_title = QLabel("Activity Log", right)
        debug_font = QFont()
        debug_font.setPointSize(11)
        debug_font.setBold(True)
        debug_title.setFont(debug_font)

        self.debug_console = QTextEdit(right)
        self.debug_console.setReadOnly(True)
        self.debug_console.setFont(QFont("Consolas", 10))

        self.btn_clear_log = QPushButton("Clear Log", right)
        self.btn_clear_log.clicked.connect(self._clear_log)

        right_layout.addWidget(debug_title)
        right_layout.addWidget(self.debug_console)
        right_layout.addWidget(self.btn_clear_log)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([600, 300])

    # ------------- Platform & dependencies -------------
    def _validate_platform(self) -> None:
        if platform.system().lower() != "windows":
            self._log("WARNING", "Non-Windows platform detected", platform.platform())
            self._show_message(
                "Platform Warning",
                "TestBuddy is designed for Windows 10/11. Some features may not work.",
                QMessageBox.Icon.Warning
            )
        if pytesseract is None:
            self._log("ERROR", "Missing dependency: pytesseract")
        if ImageGrab is None or Image is None:
            self._log("ERROR", "Missing dependency: Pillow (ImageGrab)")
        if pyperclip is None:
            self._log("WARNING", "Missing dependency: pyperclip (copy disabled)")

    # ------------- Logging -------------
    def _log(self, level: str, message: str, details: Optional[str] = None) -> None:
        line = fmt_log(level, message, details)
        # Write to file
        safe_write_log(line)
        # Buffer & GUI
        self._log_buffer.append(line)
        # Limit to last N messages
        if len(self._log_buffer) > config.log_buffer_size:
            self._log_buffer = self._log_buffer[-config.log_buffer_size:]
        self.debug_console.setPlainText("\n".join(self._log_buffer))
        self.debug_console.moveCursor(QTextCursor.MoveOperation.End)

    def _clear_log(self) -> None:
        self._log_buffer = []
        self.debug_console.clear()
        safe_write_log(fmt_log("INFO", "Log cleared"))

    # ------------- Actions -------------
    def take_screenshot(self):
        self._log("INFO", "Screenshot requested")
        self.btn_copy.setEnabled(False)
        self.text_area.clear()
        self._last_text = ""

        # Launch Snipping Tool via URI
        try:
            subprocess.Popen(['explorer.exe', 'ms-screenclip:'], shell=False)
            self._log("INFO", "Launched Snipping Tool via ms-screenclip")
        except Exception as e:
            self._log("ERROR", "Failed to launch Snipping Tool", str(e))
            self._show_message("Launch Error", f"Unable to open Snipping Tool.\n{e}", QMessageBox.Icon.Critical)
            return

        # Begin clipboard polling
        self._start_polling()

    def _start_polling(self) -> None:
        if self._polling:
            return
        self._polling = True
        self._log("DEBUG", "Clipboard polling started", f"Interval={config.clipboard_poll_interval_ms}ms")
        self._poll_clipboard()

    def _stop_polling(self) -> None:
        self._polling = False
        self._log("DEBUG", "Clipboard polling stopped")

    def _poll_clipboard(self) -> None:
        if not self._polling:
            return

        # Try to read an image from the clipboard
        found: bool = False
        try:
            if ImageGrab is not None:
                img = ImageGrab.grabclipboard()
                if img is not None:
                    found = True
        except Exception as e:
            self._log("ERROR", "Clipboard read failed", str(e))

        if found:
            self._log("INFO", "Image found in clipboard")
            self._stop_polling()
            self._run_ocr()
        else:
            self._log("DEBUG", "No image yet; retry")
            QTimer.singleShot(config.clipboard_poll_interval_ms, self._poll_clipboard)

    def _run_ocr(self) -> None:
        self._log("INFO", "OCR started")

        self.thread = QThread(self)
        self.worker = OCRWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.process_image_from_clipboard)
        self.worker.finished.connect(self.on_ocr_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_ocr_finished(self, text: str, error: str) -> None:
        if error:
            self._log("ERROR", "OCR failed", error)
            self.btn_copy.setEnabled(False)
            return

        cleaned: str = text.strip()
        self._last_text = cleaned
        self.text_area.setPlainText(cleaned)

        if cleaned:
            self._log("INFO", "OCR finished", f"chars={len(cleaned)}")
            self.btn_copy.setEnabled(True)
            
            # Add to history if enabled
            if config.enable_history:
                history_manager.add_entry(cleaned, config.ocr_language)
            
            # Auto-copy if configured
            if config.auto_copy_on_ocr:
                self.copy_text()
        else:
            self._log("WARNING", "OCR produced empty output")
            self.btn_copy.setEnabled(False)

    def copy_text(self) -> None:
        if not self._last_text:
            self._show_message("Copy Text", "No text available to copy.", QMessageBox.Icon.Warning)
            return
        try:
            if pyperclip is None:
                raise RuntimeError("pyperclip not available.")
            pyperclip.copy(self._last_text)
            self._log("INFO", "Text copied to clipboard", f"chars={len(self._last_text)}")
        except Exception as e:
            self._log("ERROR", "Copy failed", str(e))
            self._show_message("Copy Error", f"Failed to copy text.\n{e}", QMessageBox.Icon.Critical)

    def show_help(self) -> None:
        help_text: str = (
            "TestBuddy - Screenshot to Text Converter\n\n"
            "How to use:\n"
            "1. Click the round camera button (📷) or press Ctrl+Shift+S to capture screen\n"
            "2. Windows Snipping Tool opens - take a screenshot of text\n"
            "3. OCR extracts text automatically and displays it\n"
            "4. Edit if needed, then click 'COPY TEXT' (Ctrl+C) in the top right\n"
            "5. Use toolbar buttons: Help, Export Session, History\n\n"
            "Keyboard Shortcuts:\n"
            "  Ctrl+Shift+S: Take screenshot\n"
            "  Ctrl+C: Copy extracted text\n\n"
            "Requires Tesseract OCR installed on Windows.\n"
            f"Current Language: {config.ocr_language}\n"
            f"History Enabled: {config.enable_history}"
        )
        self._show_message("Help", help_text, QMessageBox.Icon.Information)

    def export_session(self) -> None:
        if not self._last_text:
            self._show_message("Export Session", "No text to export.", QMessageBox.Icon.Warning)
            return
        try:
            from pathlib import Path
            # Create export directory if needed
            export_dir = Path(config.export_directory)
            export_dir.mkdir(exist_ok=True)
            
            timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename: str = f"testbuddy_session_{timestamp}.txt"
            filepath: Path = export_dir / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self._last_text)
            self._log("INFO", "Session exported", f"File: {filepath}")
            self._show_message("Export Session", f"Session saved as {filename}", QMessageBox.Icon.Information)
        except Exception as e:
            self._log("ERROR", "Export failed", str(e))
            self._show_message("Export Error", f"Failed to export: {e}", QMessageBox.Icon.Critical)

    def show_history(self) -> None:
        if not config.enable_history:
            self._show_message("History", "History is disabled in settings.", QMessageBox.Icon.Information)
            return
        
        recent = history_manager.get_recent(10)
        if not recent:
            self._show_message("History", "No OCR history available.", QMessageBox.Icon.Information)
            return
        
        history_text: str = "Recent OCR Sessions:\n\n"
        for i, entry in enumerate(recent, 1):
            history_text += f"{i}. {entry.timestamp}\n"
            history_text += f"   Length: {entry.text_length} chars\n"
            history_text += f"   Preview: {entry.text_preview}...\n\n"
        
        self._show_message("History", history_text, QMessageBox.Icon.Information)

    # ------------- Messaging -------------
    def _show_message(self, title: str, text: str, icon: QMessageBox.Icon = QMessageBox.Icon.Information) -> None:
        msg: QMessageBox = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec()


# -----------------------------
# Entry point
# -----------------------------
def main() -> None:
    # Create log file header
    safe_write_log(fmt_log("INFO", "=== TestBuddy session start ==="))

    app = QApplication(sys.argv)

    window = SnapOCRApp()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()


# Setup notes
# - Install dependencies: pip install -r requirements.txt
# - Install Tesseract OCR on Windows and ensure it's in PATH. If not, set the path in code:
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# - Run: python main.py

# Optional enhancements
# - Add config = "--psm 6" to image_to_string for layout-aware OCR.
# - Package as an .exe using PyInstaller:
# - pip install pyinstaller
# - pyinstaller --noconfirm --onefile --windowed main.py
# - Add keyboard shortcuts:
# - Screenshot: self.btn_screenshot.setShortcut("Ctrl+Shift+S")
# - Copy: self.btn_copy.setShortcut("Ctrl+C")
