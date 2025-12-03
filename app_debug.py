"""
TestBuddy Debug Version - Catches all errors and shows them
Run this instead of app.py to see why the app is crashing
"""

import sys
import traceback
import os

# Add exception hook BEFORE any other imports
def exception_hook(exctype, value, tb):
    """Catch all unhandled exceptions"""
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print("=" * 80)
    print("FATAL ERROR - APP CRASHED:")
    print("=" * 80)
    print(error_msg)
    print("=" * 80)
    
    # Also write to file
    try:
        with open("crash_log.txt", "w", encoding="utf-8") as f:
            f.write("TestBuddy Crash Log\n")
            f.write("=" * 80 + "\n")
            f.write(error_msg)
    except:
        pass
    
    input("\nPress Enter to exit...")
    sys.exit(1)

sys.excepthook = exception_hook

print("TestBuddy Debug Mode - Starting...")
print("=" * 80)

# Test imports step by step
try:
    print("1. Testing PyQt6 imports...")
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt
    print("   ✓ PyQt6 OK")
except Exception as e:
    print(f"   ✗ PyQt6 FAILED: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

try:
    print("2. Testing config module...")
    from config import ConfigManager
    print("   ✓ config.py OK")
except Exception as e:
    print(f"   ✗ config.py FAILED: {e}")
    traceback.print_exc()
    input("Press Enter to exit...")
    sys.exit(1)

try:
    print("3. Testing history module...")
    from history import HistoryManager
    print("   ✓ history.py OK")
except Exception as e:
    print(f"   ✗ history.py FAILED: {e}")
    traceback.print_exc()
    input("Press Enter to exit...")
    sys.exit(1)

try:
    print("4. Testing export module...")
    from export import ExportManager
    print("   ✓ export.py OK")
except Exception as e:
    print(f"   ✗ export.py FAILED: {e}")
    traceback.print_exc()
    input("Press Enter to exit...")
    sys.exit(1)

try:
    print("5. Testing undo_redo module...")
    from undo_redo import UndoRedoManager
    print("   ✓ undo_redo.py OK")
except Exception as e:
    print(f"   ✗ undo_redo.py FAILED: {e}")
    traceback.print_exc()
    input("Press Enter to exit...")
    sys.exit(1)

print("\n" + "=" * 80)
print("All imports successful! Now attempting to start app...")
print("=" * 80 + "\n")

# Now import and run the actual app
try:
    print("6. Creating QApplication...")
    app = QApplication(sys.argv)
    print("   ✓ QApplication created")
    
    print("7. Importing MainWindow from app.py...")
    from app import MainWindow
    print("   ✓ MainWindow imported")
    
    print("8. Creating MainWindow instance...")
    window = MainWindow()
    print("   ✓ MainWindow created")
    
    print("9. Showing window...")
    window.show()
    print("   ✓ Window shown")
    
    print("\n" + "=" * 80)
    print("SUCCESS! App is running. Check if window is visible.")
    print("If window appears and closes immediately, there's a logic error.")
    print("=" * 80 + "\n")
    
    print("10. Starting event loop...")
    sys.exit(app.exec())
    
except Exception as e:
    print(f"\n✗ APP STARTUP FAILED: {e}")
    traceback.print_exc()
    input("\nPress Enter to exit...")
    sys.exit(1)
