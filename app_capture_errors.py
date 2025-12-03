"""
TestBuddy with Full Error Capture
==================================

This version captures ALL errors and saves them to a file
so you can copy/paste them easily.
"""

import sys
import traceback
from datetime import datetime

# Create error log file
error_log_path = "testbuddy_errors.txt"

def log_error(error_type, error_msg, error_traceback):
    """Save error to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(error_log_path, "a", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"ERROR CAPTURED: {timestamp}\n")
        f.write("=" * 80 + "\n")
        f.write(f"Type: {error_type}\n")
        f.write(f"Message: {error_msg}\n")
        f.write("\nFull Traceback:\n")
        f.write("-" * 80 + "\n")
        f.write(error_traceback)
        f.write("-" * 80 + "\n\n")
    
    print(f"\n✓ Error saved to: {error_log_path}")
    print("You can now open this file and copy the error message.")

# Set up exception hook
def exception_hook(exctype, value, tb):
    """Catch all unhandled exceptions"""
    error_msg = str(value)
    error_traceback = "".join(traceback.format_exception(exctype, value, tb))
    
    print("\n" + "=" * 80)
    print("ERROR OCCURRED!")
    print("=" * 80)
    print(f"Type: {exctype.__name__}")
    print(f"Message: {error_msg}")
    print("\nFull error has been saved to: testbuddy_errors.txt")
    print("=" * 80)
    
    log_error(exctype.__name__, error_msg, error_traceback)
    
    input("\nPress Enter to exit...")
    sys.exit(1)

sys.excepthook = exception_hook

print("TestBuddy - Error Capture Mode")
print("All errors will be saved to: testbuddy_errors.txt")
print("=" * 80)
print()

# Now import and run the app
try:
    print("Starting application...")
    from app import main
    main()
except Exception as e:
    # This will be caught by the exception hook
    raise
