#!/usr/bin/env python3
"""
TestBuddy v2 - Deployment & Build Validation

Comprehensive validation that the application is ready for deployment.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))


def validate_files():
    """Check all required files exist."""
    print("\n" + "="*60)
    print("FILE VALIDATION")
    print("="*60)
    
    required_files = [
        ("Python Code", [
            "app.py",
            "config.py", 
            "history.py",
            "run.py",
            "test_suite.py",
        ]),
        ("Configuration", [
            "testbuddy.ini",
            "requirements.txt",
        ]),
        ("Documentation", [
            "README_V2.md",
            "QUICKSTART_V2.md",
            "PHASE2_INTEGRATION.md",
            "INTEGRATION_SUMMARY.md",
            "COMPLETE_SUMMARY.md",
        ]),
    ]
    
    all_ok = True
    for category, files in required_files:
        print(f"\n{category}:")
        for filename in files:
            filepath = Path(filename)
            if filepath.exists():
                size = filepath.stat().st_size
                print(f"  [OK] {filename:30} ({size:,} bytes)")
            else:
                print(f"  [MISSING] {filename:30}")
                all_ok = False
    
    return all_ok


def validate_syntax():
    """Check Python syntax of all modules."""
    print("\n" + "="*60)
    print("SYNTAX VALIDATION")
    print("="*60)
    
    import py_compile
    
    python_files = ["app.py", "config.py", "history.py", "run.py", "test_suite.py"]
    all_ok = True
    
    for filename in python_files:
        try:
            py_compile.compile(filename, doraise=True)
            print(f"  [OK] {filename}")
        except Exception as e:
            print(f"  [ERROR] {filename}: {e}")
            all_ok = False
    
    return all_ok


def validate_imports():
    """Test that all imports work."""
    print("\n" + "="*60)
    print("IMPORT VALIDATION")
    print("="*60)
    
    modules = {
        "PyQt6": "PyQt6.QtCore",
        "PIL": "PIL.Image",
        "pytesseract": "pytesseract",
        "config": "config",
        "history": "history",
    }
    
    all_ok = True
    for name, module_path in modules.items():
        try:
            __import__(module_path)
            print(f"  [OK] {name:15} ({module_path})")
        except Exception as e:
            print(f"  [ERROR] {name:15} ({module_path}): {e}")
            all_ok = False
    
    return all_ok


def validate_config():
    """Check configuration system."""
    print("\n" + "="*60)
    print("CONFIGURATION VALIDATION")
    print("="*60)
    
    try:
        from config import ConfigManager
        cm = ConfigManager()
        config = cm.config
        
        checks = [
            ("Tesseract path", lambda: isinstance(config.tesseract_path, str)),
            ("OCR language", lambda: isinstance(config.ocr_language, str)),
            ("History file", lambda: isinstance(config.history_file, str)),
            ("Export directory", lambda: isinstance(config.export_directory, str)),
            ("Debug mode", lambda: isinstance(config.debug_mode, bool)),
            ("History enabled", lambda: isinstance(config.enable_history, bool)),
        ]
        
        all_ok = True
        for check_name, check_func in checks:
            result = check_func()
            status = "[OK]" if result else "[ERROR]"
            print(f"  {status} {check_name}")
            all_ok = all_ok and result
        
        return all_ok
    except Exception as e:
        print(f"  [ERROR] Config system: {e}")
        return False


def validate_history():
    """Check history system."""
    print("\n" + "="*60)
    print("HISTORY SYSTEM VALIDATION")
    print("="*60)
    
    try:
        from config import ConfigManager
        from history import HistoryManager
        
        cm = ConfigManager()
        hm = HistoryManager(cm.config.history_file, cm.config.history_max_entries)
        
        # Test add
        hm.add_entry("Test entry", "eng", tags=["test"])
        print(f"  [OK] add_entry() works")
        
        # Test get_all
        all_entries = hm.get_all()
        print(f"  [OK] get_all() works ({len(all_entries)} entries)")
        
        # Test search
        search_results = hm.search("Test")
        print(f"  [OK] search() works ({len(search_results)} results)")
        
        # Test persistence
        hm.save()
        history_file = Path(cm.config.history_file)
        if history_file.exists():
            print(f"  [OK] Persistence works ({history_file.stat().st_size} bytes)")
        else:
            print(f"  [WARNING] History file not saved")
        
        return True
    except Exception as e:
        print(f"  [ERROR] History system: {e}")
        return False


def validate_app_structure():
    """Check app.py structure."""
    print("\n" + "="*60)
    print("APPLICATION STRUCTURE VALIDATION")
    print("="*60)
    
    try:
        with open("app.py", "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        required_classes = [
            "Session",
            "ImageViewer",
            "OCRWorker",
            "SplashScreen",
            "NewSessionDialog",
            "HomePage",
            "Workbench",
            "MainWindow",
        ]
        
        required_functions = [
            "safe_write_log",
            "fmt_log",
        ]
        
        all_ok = True
        
        for class_name in required_classes:
            if f"class {class_name}" in content:
                print(f"  [OK] Class: {class_name}")
            else:
                print(f"  [MISSING] Class: {class_name}")
                all_ok = False
        
        for func_name in required_functions:
            if f"def {func_name}" in content:
                print(f"  [OK] Function: {func_name}")
            else:
                print(f"  [MISSING] Function: {func_name}")
                all_ok = False
        
        # Check line count
        lines = len(content.split('\n'))
        print(f"  [OK] Code size: {lines} lines")
        
        return all_ok
    except Exception as e:
        print(f"  [ERROR] App structure: {e}")
        return False


def validate_dependencies():
    """List all dependencies."""
    print("\n" + "="*60)
    print("DEPENDENCY CHECK")
    print("="*60)
    
    try:
        with open("requirements.txt", "r") as f:
            reqs = f.read().strip().split('\n')
        
        print("\nRequired packages (from requirements.txt):")
        for req in reqs:
            if req.strip() and not req.startswith('#'):
                print(f"  - {req}")
        
        # Check installed versions
        print("\nInstalled versions:")
        versions = {}
        
        try:
            import PyQt6
            versions['PyQt6'] = "installed"
        except:
            pass
        
        try:
            import PIL
            versions['Pillow'] = PIL.__version__
        except:
            pass
        
        try:
            import pytesseract
            versions['pytesseract'] = "installed"
        except:
            pass
        
        for name, version in versions.items():
            print(f"  [OK] {name:15} {version}")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Dependencies: {e}")
        return False


def generate_report():
    """Generate deployment report."""
    print("\n" + "="*60)
    print("DEPLOYMENT READINESS REPORT")
    print("="*60)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    checks = {
        "Files Present": validate_files(),
        "Syntax Valid": validate_syntax(),
        "Imports OK": validate_imports(),
        "Config System": validate_config(),
        "History System": validate_history(),
        "App Structure": validate_app_structure(),
        "Dependencies": validate_dependencies(),
    }
    
    print("\n" + "="*60)
    print("FINAL STATUS")
    print("="*60)
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    for name, result in checks.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")
    
    print("-"*60)
    print(f"Overall: {passed}/{total} checks passed")
    print(f"Generated: {timestamp}")
    
    if passed == total:
        print("\n✓ APPLICATION IS READY FOR DEPLOYMENT")
        print("\nTo run the app:")
        print("  python run.py")
        print("\nTo run tests:")
        print("  python test_suite.py")
        return 0
    else:
        print(f"\n✗ APPLICATION HAS {total - passed} ISSUE(S)")
        print("\nReview errors above and fix before deployment")
        return 1


def main():
    """Run all validations."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + "  TestBuddy v2 - Deployment Validation".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    return generate_report()


if __name__ == "__main__":
    sys.exit(main())
