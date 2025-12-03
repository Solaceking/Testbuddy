"""
TestBuddy - No Splash Screen Version (for testing)

This version skips the splash screen and shows MainWindow immediately.
Use this for testing, then switch back to app.py for production.
"""

import sys

# Import everything from app.py
from app import *

def main_nosplash():
    """Main entry point without splash screen"""
    print("Starting TestBuddy (no splash screen)...")
    
    app = QApplication(sys.argv)
    
    print("Creating MainWindow...")
    main_win = MainWindow()
    
    print("Showing MainWindow...")
    main_win.show()
    
    print("TestBuddy is now running!")
    print("Close the window to exit.\n")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main_nosplash()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
