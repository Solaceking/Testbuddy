"""
Fixed OCR Module with Comprehensive Error Handling
===================================================

This module provides robust OCR processing with detailed error reporting
"""

import time
import os
import sys
from pathlib import Path
from typing import Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal

# Import logger
from logger import get_logger

try:
    from PIL import ImageGrab, Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    ImageGrab = None
    Image = None

try:
    import pytesseract
    HAS_PYTESSERACT = True
except ImportError:
    HAS_PYTESSERACT = False
    pytesseract = None


class OCRWorkerFixed(QObject):
    """
    Improved OCR worker with comprehensive error handling and logging
    """
    finished = pyqtSignal(str, str)  # (text, error)
    progress = pyqtSignal(str)  # Status updates
    
    def __init__(self, config, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.config = config
        self.last_image: Optional[object] = None
        self.logger = get_logger()
    
    def check_dependencies(self) -> Tuple[bool, str]:
        """
        Check if all OCR dependencies are available
        
        Returns:
            (success, error_message)
        """
        # Check PIL
        if not HAS_PIL:
            return False, "Pillow (PIL) is not installed. Run: pip install Pillow"
        
        # Check pytesseract
        if not HAS_PYTESSERACT:
            return False, "pytesseract is not installed. Run: pip install pytesseract"
        
        # Check Tesseract binary
        tesseract_path = Path(self.config.tesseract_path)
        
        # Get application directory (for bundled Tesseract)
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = Path(sys._MEIPASS)
        else:
            # Running as script
            app_dir = Path(__file__).parent
        
        # Try multiple paths, prioritizing bundled version
        possible_paths = [
            app_dir / "tesseract" / "tesseract.exe",  # Bundled with app
            app_dir / ".." / "tesseract" / "tesseract.exe",  # One level up
            tesseract_path,  # Config path
            Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),  # System install
            Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
            Path(r"C:\Tesseract-OCR\tesseract.exe"),
        ]
        
        tesseract_found = False
        found_path = None
        
        for path in possible_paths:
            if path.exists():
                pytesseract.pytesseract.tesseract_cmd = str(path)
                tesseract_found = True
                found_path = path
                
                # Set TESSDATA_PREFIX if using bundled version
                if "tesseract" in str(path).lower() and (app_dir in path.parents or app_dir == path.parent.parent):
                    tessdata_dir = path.parent / "tessdata"
                    if tessdata_dir.exists():
                        # Use forward slashes for TESSDATA_PREFIX (Tesseract requirement)
                        tessdata_prefix = str(tessdata_dir.parent).replace('\\', '/')
                        os.environ['TESSDATA_PREFIX'] = tessdata_prefix
                        self.logger.info("OCR", f"Using bundled tessdata: {tessdata_dir}")
                        self.logger.debug("OCR", f"TESSDATA_PREFIX set to: {tessdata_prefix}")
                
                self.logger.info("OCR", f"✅ Tesseract found at: {path}")
                break
        
        if not tesseract_found:
            error_msg = (
                "Tesseract OCR binary not found!\n\n"
                "TestBuddy comes with bundled Tesseract, but it seems to be missing.\n\n"
                "Please try:\n"
                "1. Re-download/re-install TestBuddy\n"
                "2. Or manually install Tesseract from:\n"
                "   https://github.com/UB-Mannheim/tesseract/wiki\n\n"
                f"Expected bundled location: {app_dir / 'tesseract' / 'tesseract.exe'}\n"
                f"Or system install: C:\\Program Files\\Tesseract-OCR\\tesseract.exe\n\n"
                "After installation, restart TestBuddy."
            )
            return False, error_msg
        
        # Try to verify Tesseract works
        try:
            version = pytesseract.get_tesseract_version()
            self.logger.info("OCR", f"✅ Tesseract version: {version}")
            self.logger.info("OCR", f"✅ Tesseract path: {found_path}")
            return True, ""
        except Exception as e:
            return False, f"Tesseract found but not working: {str(e)}"
    
    def process_image_from_clipboard(self) -> None:
        """
        Process image from clipboard with comprehensive error handling
        """
        start_time = time.time()
        
        try:
            # Step 1: Check dependencies
            self.progress.emit("Checking OCR dependencies...")
            self.logger.debug("OCR", "Checking dependencies")
            
            deps_ok, deps_error = self.check_dependencies()
            if not deps_ok:
                self.logger.error("OCR", "Dependency check failed", {
                    "error": deps_error
                })
                self.finished.emit("", deps_error)
                return
            
            # Step 2: Get image from clipboard
            self.progress.emit("Reading clipboard...")
            self.logger.debug("OCR", "Reading clipboard")
            
            img = ImageGrab.grabclipboard()
            if img is None:
                error_msg = (
                    "No image found in clipboard!\n\n"
                    "Steps:\n"
                    "1. Take a screenshot (Windows Snipping Tool or Win+Shift+S)\n"
                    "2. Make sure to COPY the screenshot (Ctrl+C)\n"
                    "3. Click Capture button in TestBuddy"
                )
                self.logger.warning("OCR", "No image in clipboard")
                self.finished.emit("", error_msg)
                return
            
            # Validate it's an image
            if not isinstance(img, Image.Image):
                error_msg = "Clipboard content is not an image"
                self.logger.error("OCR", error_msg, {
                    "type": str(type(img))
                })
                self.finished.emit("", error_msg)
                return
            
            # Store image
            self.last_image = img
            image_size = img.size
            
            self.logger.log_ocr_start(image_size, self.config.ocr_language)
            
            # Step 3: Preprocess image
            self.progress.emit(f"Processing image ({image_size[0]}x{image_size[1]})...")
            self.logger.debug("OCR", "Preprocessing image", {
                "width": image_size[0],
                "height": image_size[1],
                "mode": img.mode
            })
            
            # Convert to grayscale for better OCR
            if img.mode != 'L':
                img_gray = img.convert('L')
            else:
                img_gray = img
            
            # Step 4: Run OCR
            self.progress.emit("Running OCR...")
            self.logger.debug("OCR", "Starting Tesseract", {
                "language": self.config.ocr_language,
                "psm": self.config.ocr_psm
            })
            
            # Build Tesseract config
            ocr_config = f"--psm {self.config.ocr_psm} --oem {self.config.ocr_oem}"
            
            # Run OCR
            text = pytesseract.image_to_string(
                img_gray,
                lang=self.config.ocr_language,
                config=ocr_config
            )
            
            # Step 5: Post-process
            self.progress.emit("Finalizing...")
            text = text.strip()
            
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.log_ocr_complete(len(text), duration_ms)
            
            if not text:
                warning_msg = (
                    "No text detected in image!\n\n"
                    "Possible reasons:\n"
                    "- Image contains no readable text\n"
                    "- Text is too small or blurry\n"
                    "- Language setting might be incorrect\n"
                    f"- Current language: {self.config.ocr_language}\n\n"
                    "Tips:\n"
                    "- Try a clearer screenshot\n"
                    "- Check language settings in File > Settings"
                )
                self.logger.warning("OCR", "No text detected")
                self.finished.emit("", warning_msg)
                return
            
            # Success!
            self.finished.emit(text, "")
            
        except pytesseract.TesseractNotFoundError as e:
            error_msg = (
                "Tesseract not found!\n\n"
                "Please install Tesseract OCR:\n"
                "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
                f"Error: {str(e)}"
            )
            self.logger.log_ocr_error(str(e), "TesseractNotFoundError")
            self.finished.emit("", error_msg)
            
        except pytesseract.TesseractError as e:
            error_msg = f"Tesseract processing error:\n\n{str(e)}"
            self.logger.log_ocr_error(str(e), "TesseractError")
            self.finished.emit("", error_msg)
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            
            # Save detailed error to file for user to copy
            try:
                with open("tesseract_error_details.txt", "w", encoding="utf-8") as f:
                    f.write("=" * 80 + "\n")
                    f.write("TESSERACT ERROR DETAILS\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(f"Error Type: {type(e).__name__}\n")
                    f.write(f"Error Message: {str(e)}\n\n")
                    f.write("Full Traceback:\n")
                    f.write("-" * 80 + "\n")
                    f.write(error_traceback)
                    f.write("-" * 80 + "\n\n")
                    f.write("Configuration:\n")
                    f.write(f"  Tesseract Path: {self.config.tesseract_path}\n")
                    f.write(f"  Language: {self.config.ocr_language}\n")
                    f.write(f"  PSM: {self.config.ocr_psm}\n")
                    f.write(f"  OEM: {self.config.ocr_oem}\n")
            except:
                pass
            
            error_msg = (
                f"OCR failed with unexpected error:\n\n"
                f"{type(e).__name__}: {str(e)}\n\n"
                f"Full error details saved to: tesseract_error_details.txt\n"
                f"You can open this file to see the complete error message."
            )
            self.logger.log_ocr_error(str(e), type(e).__name__)
            self.finished.emit("", error_msg)
