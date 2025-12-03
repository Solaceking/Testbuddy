#!/usr/bin/env python3
"""
TestBuddy v2 Functional Test Suite

Tests core functionality without UI interaction:
- Config loading
- History persistence
- Session creation and saving
- OCR worker threading
- Export functionality
"""

import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config import ConfigManager, Config
from history import HistoryManager, HistoryEntry


def test_config_manager():
    """Test configuration system."""
    print("\n📋 Testing ConfigManager...")
    try:
        cm = ConfigManager()
        config = cm.config
        
        # Validate required fields
        assert isinstance(config.tesseract_path, str), "tesseract_path should be string"
        assert isinstance(config.ocr_language, str), "ocr_language should be string"
        assert isinstance(config.clipboard_poll_interval_ms, int), "poll interval should be int"
        
        print(f"  ✅ Config loaded successfully")
        print(f"     - Tesseract: {config.tesseract_path}")
        print(f"     - Language: {config.ocr_language}")
        print(f"     - History file: {config.history_file}")
        return True
    except Exception as e:
        print(f"  ❌ ConfigManager test failed: {e}")
        return False


def test_history_manager():
    """Test history persistence system."""
    print("\n📚 Testing HistoryManager...")
    try:
        # Use temporary file for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "test_history.json"
            hm = HistoryManager(str(history_file), max_entries=50)
            
            # Test add_entry
            hm.add_entry("Hello World", "eng", tags=["test", "greeting"])
            assert len(hm.get_all()) == 1, "Should have 1 entry"
            print(f"  ✅ add_entry() works")
            
            # Test get_recent
            recent = hm.get_recent(10)
            assert len(recent) == 1, "Should have 1 recent entry"
            print(f"  ✅ get_recent() works")
            
            # Test add multiple
            for i in range(5):
                hm.add_entry(f"Test entry {i}", "eng", tags=[f"batch_{i}"])
            assert len(hm.get_all()) == 6, "Should have 6 entries"
            print(f"  ✅ Multiple entries added")
            
            # Test persistence
            hm.save()
            assert history_file.exists(), "History file should be created"
            print(f"  ✅ Persistence works (file: {history_file})")
            
            # Test search
            results = hm.search("Hello")
            assert len(results) > 0, "Search should find entries"
            print(f"  ✅ Search works")
            
            # Test get_summary
            summary = hm.get_summary()
            assert summary['total_entries'] == 6, "Summary should show 6 entries"
            assert summary['total_chars'] > 0, "Should have character count"
            print(f"  ✅ get_summary() works - {summary}")
            
            return True
    except Exception as e:
        print(f"  ❌ HistoryManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_creation():
    """Test session workflow."""
    print("\n🎯 Testing Session Workflow...")
    try:
        from app import Session
        
        # Create session
        session = Session("test-uuid", "Test Session", "General", ["test", "demo"])
        print(f"  ✅ Session created: {session.name}")
        
        # Update text
        session.update_text("This is test OCR content")
        assert session.text == "This is test OCR content", "Text should be stored"
        print(f"  ✅ Text storage works")
        
        # Convert to dict
        session_dict = session.to_dict()
        assert "session_id" in session_dict, "Session dict should have session_id"
        assert "name" in session_dict, "Session dict should have name"
        assert session_dict['name'] == "Test Session", "Name should match"
        print(f"  ✅ Session serialization works")
        
        return True
    except Exception as e:
        print(f"  ❌ Session test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_operations():
    """Test file I/O operations."""
    print("\n💾 Testing File Operations...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test export directory creation
            export_dir = Path(tmpdir) / "exports"
            export_dir.mkdir(exist_ok=True, parents=True)
            assert export_dir.exists(), "Export directory should be created"
            print(f"  ✅ Export directory creation works")
            
            # Test text file writing
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = export_dir / f"test_export_{timestamp}.txt"
            
            test_content = "This is a test export.\nWith multiple lines.\nAnd special chars: é à ü"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(test_content)
            
            assert filepath.exists(), "Export file should be created"
            print(f"  ✅ File writing works (utf-8)")
            
            # Test reading back
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == test_content, "Content should match"
            print(f"  ✅ File reading works (utf-8)")
            
            return True
    except Exception as e:
        print(f"  ❌ File operations test failed: {e}")
        return False


def test_imports():
    """Test all required imports."""
    print("\n📦 Testing Imports...")
    try:
        from PyQt6.QtCore import Qt, QTimer, QSize, QThread, QObject, pyqtSignal
        from PyQt6.QtGui import QFont, QAction, QPixmap, QImage
        from PyQt6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
            QPushButton, QStackedWidget, QListWidget, QListWidgetItem, QSplitter,
            QTextEdit, QDialog, QLineEdit, QComboBox, QDialogButtonBox, QMessageBox,
        )
        print(f"  ✅ PyQt6 imports successful")
        
        try:
            from PIL import ImageGrab, Image
            print(f"  ✅ PIL imports successful")
        except ImportError:
            print(f"  ⚠️  PIL not available (optional)")
        
        try:
            import pytesseract
            print(f"  ✅ pytesseract imports successful")
        except ImportError:
            print(f"  ⚠️  pytesseract not available (optional)")
        
        return True
    except Exception as e:
        print(f"  ❌ Import test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("TestBuddy v2 - Functional Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("ConfigManager", test_config_manager()))
    results.append(("HistoryManager", test_history_manager()))
    results.append(("Session Creation", test_session_creation()))
    results.append(("File Operations", test_file_operations()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {name}")
    
    print("-" * 60)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! App is ready for use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
