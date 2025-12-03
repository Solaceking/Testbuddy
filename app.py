"""
TestBuddy v2: Integrated app with UI, OCR, history, and persistence.

This module combines:
- ui_skeleton.py (UI/UX)
- config.py (settings)
- history.py (session persistence)
- OCRWorker from main.py (OCR processing)

Fully functional workflow:
  Home → New Session → Workbench (Capture + OCR + Edit) → Save → History
"""

from __future__ import annotations

import sys
import os
import time
import traceback
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from PyQt6.QtCore import Qt, QTimer, QSize, QThread, QObject, pyqtSignal
from PyQt6.QtGui import QFont, QAction, QPixmap, QImage
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QTextEdit,
    QDialog,
    QLineEdit,
    QComboBox,
    QDialogButtonBox,
    QMessageBox,
    QScrollArea,
)

from config import ConfigManager
from history import HistoryManager
from export import ExportManager
from undo_redo import UndoRedoManager
from logger import get_logger
from ocr_fixed import OCRWorkerFixed
from log_viewer import CollapsibleLogViewer

# Dependencies
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


# Session data class
class Session:
    """Represents a single OCR session."""
    
    def __init__(self, session_id: str, name: str, category: str = "General", tags: Optional[list] = None) -> None:
        self.session_id = session_id
        self.name = name
        self.category = category
        self.tags = tags or []
        self.text = ""
        self.image: Optional[object] = None
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
    
    def update_text(self, text: str) -> None:
        """Update text and modification time."""
        self.text = text
        self.modified_at = datetime.now()
    
    def set_image(self, image: object) -> None:
        """Set the OCR image."""
        self.image = image
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "session_id": self.session_id,
            "name": self.name,
            "category": self.category,
            "tags": self.tags,
            "text_preview": self.text[:100] if self.text else "",
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
        }


# Global managers
config_manager = ConfigManager()
config = config_manager.config
history_manager = HistoryManager(config.history_file, config.history_max_entries)
activity_logger = get_logger()  # Global activity logger
logger = activity_logger  # Alias for convenience


# Logging utilities
def safe_write_log(line: str) -> None:
    try:
        with open(config.log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def fmt_log(level: str, message: str, details: Optional[str] = None) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    base = f"[{ts}] [{level}] {message}"
    if details:
        base += f" | {details}"
    return base


# OCR Worker (from main.py, adapted)
class OCRWorker(QObject):
    finished = pyqtSignal(str, str)  # (text, error)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.last_image: Optional[object] = None

    def process_image_from_clipboard(self) -> None:
        start = time.time()
        try:
            if ImageGrab is None or Image is None:
                raise RuntimeError("Pillow (ImageGrab) is not available.")
            if pytesseract is None:
                raise RuntimeError("pytesseract is not available.")

            img = ImageGrab.grabclipboard()
            if img is None:
                raise RuntimeError("No image found in clipboard.")

            if not isinstance(img, Image.Image):
                raise RuntimeError("Clipboard contains non-image data.")

            # Store for display
            self.last_image = img

            if img.mode != "RGB":
                img = img.convert("RGB")
            img_gray = img.convert("L")

            ocr_config = f"--psm {config.ocr_psm} --oem {config.ocr_oem}"
            text = pytesseract.image_to_string(img_gray, lang=config.ocr_language, config=ocr_config)

            duration = round((time.time() - start) * 1000)
            self.finished.emit(text, "")
        except Exception as e:
            tb = traceback.format_exc()
            self.finished.emit("", f"{str(e)}\n{tb}")


class SplashScreen(QWidget):
    """Simple splash screen with timeout animation."""

    def __init__(self, parent: Optional[QWidget] = None, timeout_ms: int = 1600) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.timeout_ms = timeout_ms

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("TestBuddy")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Screenshot → Text, fast & simple")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        QTimer.singleShot(self.timeout_ms, self.close)


class NewSessionDialog(QDialog):
    """Dialog to create a new session name and optional metadata."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Session")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Session name (required)")

        self.category = QComboBox(self)
        self.category.addItems(["General", "Project", "Receipt", "Invoice"])

        self.tags_input = QLineEdit(self)
        self.tags_input.setPlaceholderText("Tags (comma-separated)")

        layout.addWidget(QLabel("Session name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Category (optional):"))
        layout.addWidget(self.category)
        layout.addWidget(QLabel("Tags (optional):"))
        layout.addWidget(self.tags_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Session name is required.")
            return
        if len(name) > 120:
            QMessageBox.warning(self, "Validation", "Session name is too long (max 120 chars).")
            return
        super().accept()

    def get_values(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "category": self.category.currentText(),
            "tags": [t.strip() for t in self.tags_input.text().split(",") if t.strip()],
        }


class ExportDialog(QDialog):
    """Dialog to select export formats and save exported files."""

    def __init__(self, parent: Optional[QWidget] = None, text: str = "") -> None:
        super().__init__(parent)
        self.setWindowTitle("Export Session")
        self.setMinimumWidth(400)
        self.text = text
        self.selected_formats = []

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Select export formats:"))

        # Checkboxes for each format
        self.fmt_txt = QPushButton("Text (.txt)", self)
        self.fmt_txt.setCheckable(True)
        self.fmt_txt.setChecked(True)
        
        self.fmt_pdf = QPushButton("PDF (.pdf)", self)
        self.fmt_pdf.setCheckable(True)
        self.fmt_pdf.setChecked(True)
        
        self.fmt_docx = QPushButton("Word (.docx)", self)
        self.fmt_docx.setCheckable(True)
        self.fmt_docx.setChecked(False)
        
        self.fmt_csv = QPushButton("Spreadsheet (.csv)", self)
        self.fmt_csv.setCheckable(True)
        self.fmt_csv.setChecked(False)
        
        self.fmt_html = QPushButton("Web (.html)", self)
        self.fmt_html.setCheckable(True)
        self.fmt_html.setChecked(False)
        
        self.fmt_md = QPushButton("Markdown (.md)", self)
        self.fmt_md.setCheckable(True)
        self.fmt_md.setChecked(False)
        
        self.fmt_json = QPushButton("Data (.json)", self)
        self.fmt_json.setCheckable(True)
        self.fmt_json.setChecked(False)

        # Grid layout for buttons
        fmt_layout = QVBoxLayout()
        for btn in [self.fmt_txt, self.fmt_pdf, self.fmt_docx, self.fmt_csv, 
                    self.fmt_html, self.fmt_md, self.fmt_json]:
            fmt_layout.addWidget(btn)

        layout.addLayout(fmt_layout)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self) -> None:
        self.selected_formats = []
        if self.fmt_txt.isChecked():
            self.selected_formats.append("txt")
        if self.fmt_pdf.isChecked():
            self.selected_formats.append("pdf")
        if self.fmt_docx.isChecked():
            self.selected_formats.append("docx")
        if self.fmt_csv.isChecked():
            self.selected_formats.append("csv")
        if self.fmt_html.isChecked():
            self.selected_formats.append("html")
        if self.fmt_md.isChecked():
            self.selected_formats.append("md")
        if self.fmt_json.isChecked():
            self.selected_formats.append("json")

        if not self.selected_formats:
            QMessageBox.warning(self, "Validation", "Select at least one format.")
            return

        super().accept()

    def get_formats(self) -> list:
        return self.selected_formats


class HomePage(QWidget):
    """Home / Dashboard containing New Session CTA and recent sessions with search/filter."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.all_sessions = []  # Store all sessions for filtering
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Header with New Session button
        header = QHBoxLayout()
        self.btn_new = QPushButton("+ New Session")
        self.btn_new.setMinimumHeight(40)
        header.addWidget(self.btn_new)
        header.addStretch()
        layout.addLayout(header)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search sessions by name or content... (Ctrl+F)")
        self.search_input.textChanged.connect(self.on_search_changed)
        
        self.filter_combo = QComboBox(self)
        self.filter_combo.addItems(["All Categories", "General", "Project", "Receipt", "Invoice"])
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(QLabel("Filter:"))
        search_layout.addWidget(self.filter_combo)
        layout.addLayout(search_layout)

        # Recent Sessions
        self.recent_list = QListWidget(self)
        self.recent_list.setMinimumHeight(180)
        layout.addWidget(QLabel("Recent Sessions"))
        layout.addWidget(self.recent_list)

        # All Sessions
        self.full_list = QListWidget(self)
        layout.addWidget(QLabel("All Sessions"))
        layout.addWidget(self.full_list)

    def refresh_sessions(self, sessions_data: list) -> None:
        """Load sessions from history manager."""
        self.all_sessions = sessions_data
        self.update_lists()

    def update_lists(self) -> None:
        """Update session lists based on current search/filter."""
        self.recent_list.clear()
        self.full_list.clear()

        # Get filter category
        filter_category = self.filter_combo.currentText()
        if filter_category == "All Categories":
            filter_category = None

        # Get search term
        search_term = self.search_input.text().lower().strip()

        # Filter sessions
        filtered = []
        for sess in self.all_sessions:
            # Category filter
            if filter_category and sess.get("category", "General") != filter_category:
                continue

            # Search filter (search in name and preview)
            if search_term:
                name = sess.get("name", "").lower()
                preview = sess.get("text_preview", "").lower()
                if search_term not in name and search_term not in preview:
                    continue

            filtered.append(sess)

        # Recent (first 5 of filtered)
        for sess in filtered[:5]:
            name = sess.get("name", "Untitled")
            preview = sess.get("text_preview", "")[:50]
            category = sess.get("category", "General")
            item_text = f"{name} [{category}] - {preview}"
            self.recent_list.addItem(QListWidgetItem(item_text))

        # All (full filtered list)
        for sess in filtered:
            name = sess.get("name", "Untitled")
            preview = sess.get("text_preview", "")[:50]
            category = sess.get("category", "General")
            timestamp = sess.get("created_at", "")[:10] if sess.get("created_at") else ""
            item_text = f"{name} [{category}] - {preview} ({timestamp})"
            self.full_list.addItem(QListWidgetItem(item_text))

    def on_search_changed(self, text: str) -> None:
        """Handle search input changes."""
        self.update_lists()
        if text:
            logger.info("UI", f"Search filter applied: '{text}'")

    def on_filter_changed(self, text: str) -> None:
        """Handle filter category changes."""
        self.update_lists()
        logger.info("UI", f"Category filter changed: {text}")

        # All


class Workbench(QWidget):
    """Modern OCR workspace with clean layout."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Status bar at top
        self.status_label = QLabel("Ready to capture")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                padding: 8px;
            }
        """)
        layout.addWidget(self.status_label)

        # Rich text toolbar (compact, modern)
        fmt_toolbar = QHBoxLayout()
        fmt_toolbar.setSpacing(5)
        
        self.btn_bold = QPushButton("B")
        self.btn_bold.setMaximumWidth(35)
        self.btn_bold.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 6px;
                background: white;
            }
            QPushButton:hover {
                background: #f0f0f0;
            }
        """)
        self.btn_bold.setToolTip("Bold (Ctrl+B)")
        
        self.btn_italic = QPushButton("I")
        self.btn_italic.setMaximumWidth(35)
        self.btn_italic.setStyleSheet("""
            QPushButton {
                font-style: italic;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 6px;
                background: white;
            }
            QPushButton:hover {
                background: #f0f0f0;
            }
        """)
        self.btn_italic.setToolTip("Italic (Ctrl+I)")
        
        self.btn_underline = QPushButton("U")
        self.btn_underline.setMaximumWidth(35)
        self.btn_underline.setStyleSheet("""
            QPushButton {
                text-decoration: underline;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 6px;
                background: white;
            }
            QPushButton:hover {
                background: #f0f0f0;
            }
        """)
        self.btn_underline.setToolTip("Underline (Ctrl+U)")
        
        # Font size selector
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["10pt", "12pt", "14pt", "16pt", "18pt", "20pt", "24pt"])
        self.font_size_combo.setCurrentText("14pt")
        self.font_size_combo.setMaximumWidth(80)
        self.font_size_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px 8px;
                background: white;
            }
        """)
        
        fmt_toolbar.addWidget(self.btn_bold)
        fmt_toolbar.addWidget(self.btn_italic)
        fmt_toolbar.addWidget(self.btn_underline)
        fmt_toolbar.addSpacing(10)
        fmt_toolbar.addWidget(QLabel("Size:"))
        fmt_toolbar.addWidget(self.font_size_combo)
        fmt_toolbar.addStretch()
        layout.addLayout(fmt_toolbar)

        # Text editor (large, clean)
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("OCR text will appear here automatically...")
        self.text_editor.setAcceptRichText(True)  # Enable rich text
        self.text_editor.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                font-size: 14pt;
                line-height: 1.6;
                background: white;
            }
            QTextEdit:focus {
                border: 2px solid #007AFF;
            }
        """)
        layout.addWidget(self.text_editor)

        # Bottom row: character count + action buttons
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(10)
        
        self.char_count_label = QLabel("0 characters")
        self.char_count_label.setStyleSheet("color: #666; font-size: 12px;")
        bottom_row.addWidget(self.char_count_label)
        bottom_row.addStretch()
        
        # Action buttons (at bottom, modern style)
        self.btn_capture = QPushButton("📷 Capture")
        self.btn_capture.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
            QPushButton:pressed {
                background-color: #004BB8;
            }
        """)
        
        self.btn_clear = QPushButton("🗑️ Clear")
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #FF3B30;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #D92D20;
            }
        """)
        
        self.btn_copy = QPushButton("📋 Copy All")
        self.btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #34C759;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2DA74A;
            }
        """)
        
        # Secondary action buttons
        self.btn_save = QPushButton("Save")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #007AFF;
                border: 2px solid #007AFF;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f0f8ff;
            }
        """)
        
        self.btn_export = QPushButton("Export")
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #007AFF;
                border: 2px solid #007AFF;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f0f8ff;
            }
        """)
        
        self.btn_undo = QPushButton("↶ Undo")
        self.btn_undo.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        
        self.btn_redo = QPushButton("↷ Redo")
        self.btn_redo.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        
        # Add buttons to layout
        bottom_row.addWidget(self.btn_undo)
        bottom_row.addWidget(self.btn_redo)
        bottom_row.addSpacing(10)
        bottom_row.addWidget(self.btn_save)
        bottom_row.addWidget(self.btn_export)
        bottom_row.addSpacing(20)
        bottom_row.addWidget(self.btn_capture)
        bottom_row.addWidget(self.btn_clear)
        bottom_row.addWidget(self.btn_copy)
        
        layout.addLayout(bottom_row)

        # Current session metadata
        self.current_session_id: Optional[str] = None
        self.current_session_name: Optional[str] = None
        self.current_image: Optional[object] = None

        # Initialize undo/redo manager
        self.undo_redo = UndoRedoManager(self.text_editor, max_stack_size=100)

        # Connect text editor signals
        self.text_editor.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self) -> None:
        """Update character count when text changes."""
        text = self.text_editor.toPlainText()
        char_count = len(text)
        self.char_count_label.setText(f"{char_count:,} characters")


class MainWindow(QMainWindow):
    """Main application window with stacked pages."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TestBuddy")
        self.resize(1100, 750)  # Slightly taller for log viewer

        # Central widget with log viewer at bottom
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        # Main content (stacked pages)
        self.stack = QStackedWidget()
        central_layout.addWidget(self.stack, stretch=1)

        # Pages
        self.home_page = HomePage(self)
        self.workbench = Workbench(self)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.workbench)
        
        # Log viewer at bottom (collapsible)
        self.log_viewer = CollapsibleLogViewer()
        central_layout.addWidget(self.log_viewer)
        
        self.setCentralWidget(central)

        # OCR worker thread
        self.ocr_thread: Optional[QThread] = None
        self.worker: Optional[OCRWorkerFixed] = None

        # Polling state
        self._polling = False

        # Current session
        self.current_session: Optional[Session] = None

        # Menu / actions
        self._create_actions()

        # Wire interactions
        self.home_page.btn_new.clicked.connect(self.on_new_session)
        self.home_page.recent_list.itemDoubleClicked.connect(self.open_session_from_item)
        self.home_page.full_list.itemDoubleClicked.connect(self.open_session_from_item)

        self.workbench.btn_capture.clicked.connect(self.on_capture)
        self.workbench.btn_save.clicked.connect(self.on_save_session)
        self.workbench.btn_export.clicked.connect(self.on_export_session)
        self.workbench.btn_undo.clicked.connect(self.on_undo)
        self.workbench.btn_redo.clicked.connect(self.on_redo)
        self.workbench.btn_clear.clicked.connect(self.on_clear_text)
        self.workbench.btn_copy.clicked.connect(self.on_copy_all)
        
        # Formatting toolbar connections
        self.workbench.btn_bold.clicked.connect(self.on_format_bold)
        self.workbench.btn_italic.clicked.connect(self.on_format_italic)
        self.workbench.btn_underline.clicked.connect(self.on_format_underline)
        self.workbench.font_size_combo.currentTextChanged.connect(self.on_font_size_changed)

        # Keyboard shortcuts
        self.new_action.setShortcut("Ctrl+N")
        self.save_action.setShortcut("Ctrl+S")

        # Load initial sessions
        self.load_sessions_to_home()

        # Logging
        safe_write_log(fmt_log("INFO", "TestBuddy v2 started"))

    def _create_actions(self) -> None:
        menubar = self.menuBar()
        if menubar is None:
            return

        file_menu = menubar.addMenu("File")
        if file_menu is None:
            return

        self.new_action = QAction("New Session", self)
        file_menu.addAction(self.new_action)
        self.new_action.triggered.connect(self.on_new_session)

        self.save_action = QAction("Save", self)
        file_menu.addAction(self.save_action)
        self.save_action.triggered.connect(self.on_save_session)

        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        file_menu.addAction(exit_action)
        exit_action.triggered.connect(self.close)

        view_menu = menubar.addMenu("View")
        if view_menu is None:
            return
        home_act = QAction("Home", self)
        home_act.triggered.connect(self.go_home)
        view_menu.addAction(home_act)

    def load_sessions_to_home(self) -> None:
        """Load all sessions from history manager and populate home page."""
        if not config.enable_history:
            return
        sessions = history_manager.get_all()
        sessions_data = [
            {
                "name": s.timestamp.split("T")[0],  # Use date as name for now
                "text_preview": s.text_preview,
                "full_text": s.full_text,
            }
            for s in sessions
        ]
        self.home_page.refresh_sessions(sessions_data)
        logger.info("SESSION", f"Loaded {len(sessions)} sessions to home page")

    def on_new_session(self) -> None:
        activity_logger.log_ui_action("new_session_button_clicked")
        dlg = NewSessionDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            vals = dlg.get_values()
            name: str = vals.get("name", "Untitled")
            category: str = vals.get("category", "General")
            tags: list = vals.get("tags", [])
            
            # Create session
            self.current_session = Session(str(uuid4()), name, category, tags)
            
            # Update workbench
            self.workbench.current_session_id = self.current_session.session_id
            self.workbench.current_session_name = self.current_session.name
            self.workbench.text_editor.clear()
            self.workbench.status_label.setText(f"Session: {name}")
            self.stack.setCurrentWidget(self.workbench)
            safe_write_log(fmt_log("INFO", "New session created", f"name={name}, category={category}"))
            activity_logger.log_session_created(self.current_session.session_id, name)
            activity_logger.info("UI", "Navigated to workbench", {"session_name": name, "category": category})

    def open_session_from_item(self, item: QListWidgetItem) -> None:
        text = item.text()
        activity_logger.log_ui_action("session_opened_from_list", {"session": text[:50]})
        self.workbench.current_session_name = text
        self.workbench.text_editor.setPlainText(f"{text}\n\n(loaded from history)")
        self.workbench.status_label.setText(f"Session: {text}")
        self.stack.setCurrentWidget(self.workbench)
        safe_write_log(fmt_log("INFO", "Session opened", f"name={text}"))
        activity_logger.info("SESSION", "Session loaded from history")

    def on_capture(self) -> None:
        activity_logger.log_ui_action("capture_button_clicked")
        
        # Auto-clear text if there's existing content
        if self.workbench.text_editor.toPlainText().strip():
            self.workbench.text_editor.clear()
            logger.info("UI", "Auto-cleared text for new capture")
        
        self.workbench.status_label.setText("Launching Snipping Tool...")
        safe_write_log(fmt_log("INFO", "Capture initiated"))
        activity_logger.info("CAPTURE", "Screenshot capture initiated")

        try:
            subprocess.Popen(["explorer.exe", "ms-screenclip:"], shell=False)
        except Exception as e:
            self.workbench.status_label.setText("Failed to launch Snipping Tool")
            safe_write_log(fmt_log("ERROR", "Failed to launch Snipping Tool", str(e)))
            return

        self._start_polling()

    def _start_polling(self) -> None:
        if self._polling:
            return
        self._polling = True
        self._poll_clipboard()

    def _stop_polling(self) -> None:
        self._polling = False

    def _poll_clipboard(self) -> None:
        if not self._polling:
            return

        found = False
        try:
            if ImageGrab is not None:
                img = ImageGrab.grabclipboard()
                if img is not None:
                    found = True
        except Exception as e:
            safe_write_log(fmt_log("ERROR", "Clipboard read failed", str(e)))

        if found:
            self.workbench.status_label.setText("Image found, processing OCR...")
            self._stop_polling()
            self._run_ocr()
        else:
            QTimer.singleShot(config.clipboard_poll_interval_ms, self._poll_clipboard)

    def _run_ocr(self) -> None:
        self.ocr_thread = QThread(self)
        self.worker = OCRWorkerFixed(config)  # Use fixed version with error handling
        self.worker.moveToThread(self.ocr_thread)
        self.ocr_thread.started.connect(self.worker.process_image_from_clipboard)
        self.worker.finished.connect(self.on_ocr_finished)
        self.worker.finished.connect(self.ocr_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.ocr_thread.finished.connect(self.ocr_thread.deleteLater)
        self.ocr_thread.start()

    def on_ocr_finished(self, text: str, error: str) -> None:
        if error:
            self.workbench.status_label.setText("OCR failed - check Activity Log below")
            safe_write_log(fmt_log("ERROR", "OCR failed", error))
            
            # Show error in log viewer (auto-expands)
            self.log_viewer.show_error(error)
            
            # Also show popup for critical errors
            QMessageBox.critical(self, "OCR Error", 
                f"{error}\n\nDetailed logs are shown below. Click 'Copy All' to copy error details.")
            return

        cleaned = text.strip()
        self.workbench.text_editor.setPlainText(cleaned)
        self.workbench.status_label.setText(f"OCR complete ({len(cleaned)} chars)")
        
        # Store image reference (no display needed)
        if self.worker and hasattr(self.worker, 'last_image') and self.worker.last_image:
            self.workbench.current_image = self.worker.last_image
        
        safe_write_log(fmt_log("INFO", "OCR finished", f"chars={len(cleaned)}"))

    def on_save_session(self) -> None:
        text = self.workbench.text_editor.toPlainText()
        
        if not text.strip():
            QMessageBox.warning(self, "Save", "No text to save.")
            return

        try:
            # Update current session
            if self.current_session:
                self.current_session.update_text(text)
                name = self.current_session.name
                session_dict = self.current_session.to_dict()
            else:
                name = "Untitled"
            
            # Save to history
            if config.enable_history:
                history_manager.add_entry(text, config.ocr_language, tags=[name])
            
            self.workbench.status_label.setText("Session saved")
            safe_write_log(fmt_log("INFO", "Session saved", f"name={name}, chars={len(text)}"))
            self.load_sessions_to_home()
            QMessageBox.information(self, "Save", f"Session '{name}' saved successfully.")
        except Exception as e:
            self.workbench.status_label.setText("Save failed")
            safe_write_log(fmt_log("ERROR", "Save failed", str(e)))
            QMessageBox.critical(self, "Error", f"Failed to save session: {e}")

    def on_export_session(self) -> None:
        text = self.workbench.text_editor.toPlainText()
        
        if not text.strip():
            QMessageBox.warning(self, "Export", "No text to export.")
            return

        name = self.current_session.name if self.current_session else "export"

        # Show export dialog
        export_dialog = ExportDialog(self, text)
        if export_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        formats = export_dialog.get_formats()
        
        try:
            # Prepare metadata
            metadata = {
                "session_name": name,
                "language": config.ocr_language,
                "category": self.current_session.category if self.current_session else "General",
                "tags": self.current_session.tags if self.current_session else [],
                "created_at": self.current_session.created_at.isoformat() if self.current_session else datetime.now().isoformat()
            }

            # Initialize export manager
            export_mgr = ExportManager(Path(config.export_directory))

            # Get image if available
            image = self.current_session.image if self.current_session else None

            # Export to selected formats
            results = export_mgr.export_all_formats(
                text=text,
                name=name,
                image=image,
                metadata=metadata,
                formats=formats
            )

            if results:
                files_str = ", ".join([p.name for p in results.values()])
                self.workbench.status_label.setText(f"Exported: {files_str}")
                safe_write_log(fmt_log("INFO", "Session exported", f"formats={','.join(formats)}, count={len(results)}"))
                
                msg = f"Session exported to {len(results)} format(s):\n"
                msg += "\n".join([f"- {p.name}" for p in results.values()])
                QMessageBox.information(self, "Export Successful", msg)
            else:
                self.workbench.status_label.setText("Export failed")
                QMessageBox.warning(self, "Export", "No formats were exported.")
        except Exception as e:
            self.workbench.status_label.setText("Export failed")
            safe_write_log(fmt_log("ERROR", "Export failed", str(e)))
            QMessageBox.critical(self, "Error", f"Failed to export session: {e}")

    def on_undo(self) -> None:
        """Undo the last text edit."""
        if self.workbench.undo_redo.can_undo():
            self.workbench.undo_redo.undo()
            self.workbench.status_label.setText("Undo")
            safe_write_log(fmt_log("INFO", "Text undo", ""))

    def on_redo(self) -> None:
        """Redo the last undone text edit."""
        if self.workbench.undo_redo.can_redo():
            self.workbench.undo_redo.redo()
            self.workbench.status_label.setText("Redo")
            safe_write_log(fmt_log("INFO", "Text redo", ""))

    def on_clear_text(self) -> None:
        """Clear all text in the editor."""
        self.workbench.text_editor.clear()
        self.workbench.status_label.setText("Text cleared")
        logger.info("UI", "Text editor cleared")

    def on_copy_all(self) -> None:
        """Copy all text to clipboard."""
        text = self.workbench.text_editor.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "Copy All", "No text to copy!")
            return
        
        try:
            if pyperclip:
                pyperclip.copy(text)
                self.workbench.status_label.setText(f"Copied {len(text)} characters to clipboard")
                logger.info("UI", f"Copied all text to clipboard: {len(text)} characters")
            else:
                # Fallback to Qt clipboard
                clipboard = QApplication.clipboard()
                if clipboard:
                    clipboard.setText(text)
                    self.workbench.status_label.setText(f"Copied {len(text)} characters")
                    logger.info("UI", f"Copied all text: {len(text)} characters")
        except Exception as e:
            QMessageBox.warning(self, "Copy Failed", f"Failed to copy text: {str(e)}")
            logger.error("UI", f"Copy all failed: {str(e)}")

    def on_format_bold(self) -> None:
        """Apply bold formatting to selected text."""
        fmt = self.workbench.text_editor.currentCharFormat()
        is_bold = fmt.fontWeight() != 700
        fmt.setFontWeight(700 if is_bold else 400)
        self.workbench.text_editor.mergeCurrentCharFormat(fmt)
        self.workbench.status_label.setText("Bold toggled")
        logger.info("UI", f"Text formatting: Bold {'enabled' if is_bold else 'disabled'}")

    def on_format_italic(self) -> None:
        """Apply italic formatting to selected text."""
        fmt = self.workbench.text_editor.currentCharFormat()
        is_italic = not fmt.fontItalic()
        fmt.setFontItalic(is_italic)
        self.workbench.text_editor.mergeCurrentCharFormat(fmt)
        self.workbench.status_label.setText("Italic toggled")
        logger.info("UI", f"Text formatting: Italic {'enabled' if is_italic else 'disabled'}")

    def on_format_underline(self) -> None:
        """Apply underline formatting to selected text."""
        fmt = self.workbench.text_editor.currentCharFormat()
        is_underline = not fmt.fontUnderline()
        fmt.setFontUnderline(is_underline)
        self.workbench.text_editor.mergeCurrentCharFormat(fmt)
        self.workbench.status_label.setText("Underline toggled")
        logger.info("UI", f"Text formatting: Underline {'enabled' if is_underline else 'disabled'}")

    def on_font_size_changed(self, size_text: str) -> None:
        """Change font size."""
        try:
            size = int(size_text.replace("pt", ""))
            fmt = self.workbench.text_editor.currentCharFormat()
            fmt.setFontPointSize(size)
            self.workbench.text_editor.mergeCurrentCharFormat(fmt)
            logger.info("UI", f"Font size changed to {size}pt")
            self.workbench.status_label.setText(f"Font size: {size}pt")
        except ValueError:
            pass

    def go_home(self) -> None:
        self.load_sessions_to_home()
        self.stack.setCurrentWidget(self.home_page)
        logger.info("UI", "Navigation: Returned to home page")


def main() -> None:
    app = QApplication(sys.argv)
    
    # Initialize logger
    logger = get_logger()
    logger.info("APPLICATION", "TestBuddy starting", {
        "version": "3.0",
        "platform": platform.system()
    })
    
    # Create main window first
    main_win = MainWindow()
    
    # Show splash screen
    splash = SplashScreen(timeout_ms=900)
    splash.show()
    
    # Show main window after splash closes
    QTimer.singleShot(950, main_win.show)  # Slightly longer to ensure splash closes first
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
