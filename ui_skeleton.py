"""
Minimal Microsoft-style UI skeleton for TestBuddy.

This module provides a runnable PyQt6 UI skeleton with:
- Splash screen
- Home page (New Session, Recent Sessions)
- New Session dialog
- Workbench (image viewer placeholder + rich text editor)

Keep it intentionally simple and easy to extend.
"""

from __future__ import annotations

import sys
from typing import Optional

from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QAction
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
)


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


class HomePage(QWidget):
    """Home / Dashboard containing New Session CTA and recent sessions."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        header = QHBoxLayout()
        self.btn_new = QPushButton("+ New Session")
        self.btn_new.setMinimumHeight(40)
        header.addWidget(self.btn_new)
        header.addStretch()
        layout.addLayout(header)

        self.recent_list = QListWidget(self)
        self.recent_list.setMinimumHeight(200)
        layout.addWidget(QLabel("Recent Sessions"))
        layout.addWidget(self.recent_list)

        self.full_list = QListWidget(self)
        layout.addWidget(QLabel("All Sessions"))
        layout.addWidget(self.full_list)

        # placeholder sample data
        for i in range(3):
            item = QListWidgetItem(f"Session {i+1} - {'Receipt' if i%2==0 else 'Notes'}")
            self.recent_list.addItem(item)
            self.full_list.addItem(QListWidgetItem(f"Session {i+1}"))


class Workbench(QWidget):
    """Capture & edit workspace: image viewer + rich text editor."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        toolbar = QHBoxLayout()
        self.btn_capture = QPushButton("Capture")
        self.btn_save = QPushButton("Save")
        toolbar.addWidget(self.btn_capture)
        toolbar.addWidget(self.btn_save)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # Left: image placeholder
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.image_label = QLabel("[Image Viewer]")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(QSize(320, 240))
        left_layout.addWidget(self.image_label)

        # Right: rich text editor
        right = QWidget()
        right_layout = QVBoxLayout(right)
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("OCR result appears here. Edit as needed.")
        right_layout.addWidget(self.text_editor)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([420, 580])

        layout.addWidget(splitter)


class MainWindow(QMainWindow):
    """Main application window with stacked pages."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TestBuddy")
        self.resize(1100, 720)

        # Central stacked widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.home_page = HomePage(self)
        self.workbench = Workbench(self)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.workbench)

        # Menu / actions
        self._create_actions()

        # Wire interactions
        self.home_page.btn_new.clicked.connect(self.on_new_session)
        self.home_page.recent_list.itemDoubleClicked.connect(self.open_session_from_item)
        self.workbench.btn_capture.clicked.connect(self.on_capture)

        # Keyboard shortcuts
        self.new_action.setShortcut("Ctrl+N")
        self.save_action.setShortcut("Ctrl+S")

    def _create_actions(self) -> None:
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        self.new_action = QAction("New Session", self)
        file_menu.addAction(self.new_action)
        self.new_action.triggered.connect(self.on_new_session)

        self.save_action = QAction("Save", self)
        file_menu.addAction(self.save_action)
        self.save_action.triggered.connect(self.on_save)

        view_menu = menubar.addMenu("View")
        home_act = QAction("Home", self)
        home_act.triggered.connect(lambda: self.stack.setCurrentWidget(self.home_page))
        view_menu.addAction(home_act)
        work_act = QAction("Workbench", self)
        work_act.triggered.connect(lambda: self.stack.setCurrentWidget(self.workbench))
        view_menu.addAction(work_act)

    def on_new_session(self) -> None:
        dlg = NewSessionDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            vals = dlg.get_values()
            name = vals.get("name")
            # Minimal behavior: create session list item and open workbench
            self.home_page.full_list.addItem(QListWidgetItem(name))
            self.home_page.recent_list.insertItem(0, QListWidgetItem(name))
            self.stack.setCurrentWidget(self.workbench)

    def open_session_from_item(self, item: QListWidgetItem) -> None:
        # For now, just open workbench and populate editor with placeholder
        self.stack.setCurrentWidget(self.workbench)
        self.workbench.text_editor.setPlainText(f"Loaded session: {item.text()}\n\n(ocr text placeholder)")

    def on_capture(self) -> None:
        # Stub for launching capture; show temporary placeholder text
        self.workbench.image_label.setText("[Captured image placeholder]")
        self.workbench.text_editor.setPlainText("Recognizing...\n\nSample OCR text")

    def on_save(self) -> None:
        # Minimal save: just show a confirmation
        QMessageBox.information(self, "Save", "Session saved (placeholder)")


def main() -> None:
    app = QApplication(sys.argv)
    splash = SplashScreen(timeout_ms=900)
    splash.show()

    # Show main window after splash hides
    main_win = MainWindow()

    # Wait for splash to close and then show main window
    QTimer.singleShot(900, main_win.show)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
