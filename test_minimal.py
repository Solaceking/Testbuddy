"""
Minimal TestBuddy - Test if basic PyQt6 window works
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class MinimalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TestBuddy - Minimal Test")
        self.setGeometry(100, 100, 600, 400)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        # Label
        label = QLabel("✓ TestBuddy Window Test")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
        layout.addWidget(label)
        
        # Info
        info = QLabel("If you see this window, PyQt6 is working correctly!\n\nThe issue is in app.py startup logic.")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(info)
        
        # Button
        btn = QPushButton("Close")
        btn.clicked.connect(self.close)
        btn.setStyleSheet("padding: 10px; font-size: 14px;")
        layout.addWidget(btn)

def main():
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    
    print("Creating window...")
    window = MinimalWindow()
    
    print("Showing window...")
    window.show()
    
    print("SUCCESS! Window should be visible now.")
    print("If window opens and stays open, PyQt6 is working.")
    print("Press the Close button or close the window to exit.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
