"""
Collapsible Log Viewer Widget for TestBuddy
===========================================

Provides a collapsible panel showing activity logs with:
- Real-time log display
- Copy to clipboard functionality
- Auto-scroll to latest entries
- Filter by log level
- Clear logs button
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTextEdit, QLabel, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from typing import Optional
from logger import get_logger, LogLevel


class CollapsibleLogViewer(QWidget):
    """
    Collapsible log viewer that can be shown/hidden
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = get_logger()
        self.is_collapsed = True
        self.auto_scroll = True
        
        self.setup_ui()
        
        # Update timer (refresh logs every 500ms)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_logs)
        self.update_timer.start(500)
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #D2D2D7;")
        layout.addWidget(separator)
        
        # Header bar with toggle button
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #F5F5F7;
                border-bottom: 1px solid #D2D2D7;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)
        
        # Toggle button
        self.toggle_btn = QPushButton("▶ Show Activity Log")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                text-align: left;
                font-weight: bold;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #E5E5EA;
                border-radius: 4px;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_collapsed)
        header_layout.addWidget(self.toggle_btn)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #6E6E73; font-size: 12px;")
        header_layout.addWidget(self.status_label)
        
        header_layout.addStretch()
        
        # Copy button
        self.copy_btn = QPushButton("Copy All")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_logs_to_clipboard)
        header_layout.addWidget(self.copy_btn)
        
        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF3B30;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_logs)
        header_layout.addWidget(self.clear_btn)
        
        layout.addWidget(header)
        
        # Log content (initially hidden)
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(12, 12, 12, 12)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.level_filter = QComboBox()
        self.level_filter.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_filter.currentTextChanged.connect(self.refresh_logs)
        filter_layout.addWidget(self.level_filter)
        
        filter_layout.addStretch()
        
        # Auto-scroll checkbox
        self.auto_scroll_btn = QPushButton("Auto-scroll: ON")
        self.auto_scroll_btn.setCheckable(True)
        self.auto_scroll_btn.setChecked(True)
        self.auto_scroll_btn.clicked.connect(self.toggle_auto_scroll)
        self.auto_scroll_btn.setStyleSheet("""
            QPushButton {
                background-color: #34C759;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:checked {
                background-color: #8E8E93;
            }
        """)
        filter_layout.addWidget(self.auto_scroll_btn)
        
        content_layout.addLayout(filter_layout)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        self.log_text.setMaximumHeight(400)
        
        # Monospace font for logs
        font = QFont("Consolas", 9)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.log_text.setFont(font)
        
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1C1C1E;
                color: #00FF00;
                border: 1px solid #D2D2D7;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        content_layout.addWidget(self.log_text)
        
        # Initially hide content
        self.content_widget.setVisible(False)
        layout.addWidget(self.content_widget)
    
    def toggle_collapsed(self):
        """Toggle between collapsed and expanded states"""
        self.is_collapsed = not self.is_collapsed
        self.content_widget.setVisible(not self.is_collapsed)
        
        if self.is_collapsed:
            self.toggle_btn.setText("▶ Show Activity Log")
        else:
            self.toggle_btn.setText("▼ Hide Activity Log")
            self.refresh_logs()
    
    def toggle_auto_scroll(self):
        """Toggle auto-scroll feature"""
        self.auto_scroll = self.auto_scroll_btn.isChecked()
        if self.auto_scroll:
            self.auto_scroll_btn.setText("Auto-scroll: ON")
            self.auto_scroll_btn.setStyleSheet("""
                QPushButton {
                    background-color: #34C759;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                }
            """)
        else:
            self.auto_scroll_btn.setText("Auto-scroll: OFF")
            self.auto_scroll_btn.setStyleSheet("""
                QPushButton {
                    background-color: #8E8E93;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                }
            """)
    
    def refresh_logs(self):
        """Refresh log display from logger"""
        if self.is_collapsed:
            return
        
        # Get filter level
        filter_text = self.level_filter.currentText()
        level_filter = None if filter_text == "ALL" else LogLevel[filter_text]
        
        # Get logs
        logs = self.logger.get_recent_logs(count=100, level=level_filter)
        
        # Format logs
        log_lines = []
        for entry in logs:
            # Color code by level
            if entry.level == "ERROR" or entry.level == "CRITICAL":
                color = "#FF3B30"  # Red
            elif entry.level == "WARNING":
                color = "#FF9500"  # Orange
            elif entry.level == "INFO":
                color = "#00FF00"  # Green
            else:
                color = "#8E8E93"  # Gray
            
            timestamp = entry.timestamp.split('T')[1].split('.')[0]  # Just time
            line = f'<span style="color: {color};">[{timestamp}] [{entry.level:8s}] {entry.category}: {entry.message}</span>'
            
            if entry.details:
                for key, value in entry.details.items():
                    line += f'<br><span style="color: #5AC8FA;">  {key}: {value}</span>'
            
            log_lines.append(line)
        
        # Update text
        html_content = '<br>'.join(log_lines)
        self.log_text.setHtml(html_content)
        
        # Auto-scroll to bottom
        if self.auto_scroll:
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        
        # Update status
        stats = self.logger.get_statistics()
        total = stats.get('total_logs', 0)
        errors = stats.get('by_level', {}).get('ERROR', 0)
        warnings = stats.get('by_level', {}).get('WARNING', 0)
        
        self.status_label.setText(f"Logs: {total} | Errors: {errors} | Warnings: {warnings}")
    
    def copy_logs_to_clipboard(self):
        """Copy all logs to clipboard"""
        try:
            import pyperclip
            
            # Get all logs as plain text
            logs = self.logger.get_recent_logs(count=200)
            log_lines = []
            
            for entry in logs:
                line = f"[{entry.timestamp}] [{entry.level:8s}] {entry.category}: {entry.message}"
                if entry.details:
                    for key, value in entry.details.items():
                        line += f"\n  {key}: {value}"
                log_lines.append(line)
            
            text = "\n".join(log_lines)
            pyperclip.copy(text)
            
            # Show feedback
            original_text = self.copy_btn.text()
            self.copy_btn.setText("✓ Copied!")
            QTimer.singleShot(2000, lambda: self.copy_btn.setText(original_text))
            
        except Exception as e:
            self.status_label.setText(f"Copy failed: {str(e)}")
    
    def clear_logs(self):
        """Clear log display"""
        self.logger.log_buffer.clear()
        self.log_text.clear()
        self.status_label.setText("Logs cleared")
    
    def show_error(self, error_message: str):
        """
        Show a specific error and expand the log viewer
        """
        # Expand if collapsed
        if self.is_collapsed:
            self.toggle_collapsed()
        
        # Log the error
        self.logger.error("USER_ERROR", error_message)
        
        # Refresh to show it
        self.refresh_logs()
