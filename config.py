"""
Configuration management for TestBuddy.
Handles INI-based settings with sensible defaults and validation.
"""

import configparser
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration container with type-safe access."""
    
    # Tesseract settings
    tesseract_path: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    ocr_language: str = "eng"  # ISO 639-3 codes, comma-separated for multiple
    ocr_psm: int = 6  # Page Segmentation Mode
    ocr_oem: int = 3  # OCR Engine Mode
    
    # UI settings
    window_width: int = 900
    window_height: int = 600
    window_always_on_top: bool = True
    theme: str = "light"  # "light" or "dark"
    splitter_ratio: int = 600  # Left panel width in pixels
    
    # Behavior settings
    clipboard_poll_interval_ms: int = 500
    log_buffer_size: int = 100
    auto_copy_on_ocr: bool = False
    
    # History settings
    enable_history: bool = True
    history_max_entries: int = 100
    history_file: str = "testbuddy_history.json"
    
    # Export settings
    export_format: str = "txt"  # "txt", "json", "csv"
    export_directory: str = "exports"
    
    # Logging
    log_file: str = "testbuddy_debug.log"
    debug_mode: bool = False


class ConfigManager:
    """Manages loading, saving, and validating configuration."""
    
    CONFIG_FILE = "testbuddy.ini"
    
    def __init__(self):
        self.config = Config()
        self.config_path = Path(self.CONFIG_FILE)
        self.load()
    
    def load(self) -> None:
        """Load configuration from INI file or create with defaults."""
        if self.config_path.exists():
            self._load_from_file()
        else:
            self._create_default_config()
    
    def _load_from_file(self) -> None:
        """Parse INI file and update config."""
        parser = configparser.ConfigParser()
        try:
            parser.read(self.config_path, encoding="utf-8")
            
            # Tesseract section
            if parser.has_section("tesseract"):
                self.config.tesseract_path = parser.get(
                    "tesseract", "path", fallback=self.config.tesseract_path
                )
                self.config.ocr_language = parser.get(
                    "tesseract", "language", fallback=self.config.ocr_language
                )
                self.config.ocr_psm = parser.getint(
                    "tesseract", "psm", fallback=self.config.ocr_psm
                )
                self.config.ocr_oem = parser.getint(
                    "tesseract", "oem", fallback=self.config.ocr_oem
                )
            
            # UI section
            if parser.has_section("ui"):
                self.config.window_width = parser.getint(
                    "ui", "window_width", fallback=self.config.window_width
                )
                self.config.window_height = parser.getint(
                    "ui", "window_height", fallback=self.config.window_height
                )
                self.config.window_always_on_top = parser.getboolean(
                    "ui", "window_always_on_top", fallback=self.config.window_always_on_top
                )
                self.config.theme = parser.get(
                    "ui", "theme", fallback=self.config.theme
                )
                self.config.splitter_ratio = parser.getint(
                    "ui", "splitter_ratio", fallback=self.config.splitter_ratio
                )
            
            # Behavior section
            if parser.has_section("behavior"):
                self.config.clipboard_poll_interval_ms = parser.getint(
                    "behavior", "clipboard_poll_interval_ms",
                    fallback=self.config.clipboard_poll_interval_ms
                )
                self.config.log_buffer_size = parser.getint(
                    "behavior", "log_buffer_size", fallback=self.config.log_buffer_size
                )
                self.config.auto_copy_on_ocr = parser.getboolean(
                    "behavior", "auto_copy_on_ocr", fallback=self.config.auto_copy_on_ocr
                )
            
            # History section
            if parser.has_section("history"):
                self.config.enable_history = parser.getboolean(
                    "history", "enable_history", fallback=self.config.enable_history
                )
                self.config.history_max_entries = parser.getint(
                    "history", "max_entries", fallback=self.config.history_max_entries
                )
                self.config.history_file = parser.get(
                    "history", "file", fallback=self.config.history_file
                )
            
            # Export section
            if parser.has_section("export"):
                self.config.export_format = parser.get(
                    "export", "format", fallback=self.config.export_format
                )
                self.config.export_directory = parser.get(
                    "export", "directory", fallback=self.config.export_directory
                )
            
            # Logging section
            if parser.has_section("logging"):
                self.config.log_file = parser.get(
                    "logging", "file", fallback=self.config.log_file
                )
                self.config.debug_mode = parser.getboolean(
                    "logging", "debug_mode", fallback=self.config.debug_mode
                )
        
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default INI file."""
        parser = configparser.ConfigParser()
        
        parser["tesseract"] = {
            "path": self.config.tesseract_path,
            "language": self.config.ocr_language,
            "psm": str(self.config.ocr_psm),
            "oem": str(self.config.ocr_oem),
        }
        
        parser["ui"] = {
            "window_width": str(self.config.window_width),
            "window_height": str(self.config.window_height),
            "window_always_on_top": str(self.config.window_always_on_top),
            "theme": self.config.theme,
            "splitter_ratio": str(self.config.splitter_ratio),
        }
        
        parser["behavior"] = {
            "clipboard_poll_interval_ms": str(self.config.clipboard_poll_interval_ms),
            "log_buffer_size": str(self.config.log_buffer_size),
            "auto_copy_on_ocr": str(self.config.auto_copy_on_ocr),
        }
        
        parser["history"] = {
            "enable_history": str(self.config.enable_history),
            "max_entries": str(self.config.history_max_entries),
            "file": self.config.history_file,
        }
        
        parser["export"] = {
            "format": self.config.export_format,
            "directory": self.config.export_directory,
        }
        
        parser["logging"] = {
            "file": self.config.log_file,
            "debug_mode": str(self.config.debug_mode),
        }
        
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                parser.write(f)
        except Exception as e:
            print(f"Error creating config file: {e}")
    
    def save(self) -> None:
        """Save current configuration to INI file."""
        parser = configparser.ConfigParser()
        
        parser["tesseract"] = {
            "path": self.config.tesseract_path,
            "language": self.config.ocr_language,
            "psm": str(self.config.ocr_psm),
            "oem": str(self.config.ocr_oem),
        }
        
        parser["ui"] = {
            "window_width": str(self.config.window_width),
            "window_height": str(self.config.window_height),
            "window_always_on_top": str(self.config.window_always_on_top),
            "theme": self.config.theme,
            "splitter_ratio": str(self.config.splitter_ratio),
        }
        
        parser["behavior"] = {
            "clipboard_poll_interval_ms": str(self.config.clipboard_poll_interval_ms),
            "log_buffer_size": str(self.config.log_buffer_size),
            "auto_copy_on_ocr": str(self.config.auto_copy_on_ocr),
        }
        
        parser["history"] = {
            "enable_history": str(self.config.enable_history),
            "max_entries": str(self.config.history_max_entries),
            "file": self.config.history_file,
        }
        
        parser["export"] = {
            "format": self.config.export_format,
            "directory": self.config.export_directory,
        }
        
        parser["logging"] = {
            "file": self.config.log_file,
            "debug_mode": str(self.config.debug_mode),
        }
        
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                parser.write(f)
        except Exception as e:
            print(f"Error saving config: {e}")
