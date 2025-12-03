"""
Advanced Activity Logger for TestBuddy
======================================

Provides comprehensive, structured logging with:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File rotation (auto-rotate when size limit reached)
- Session-based activity tracking
- Export capabilities for diagnostics
- Real-time log viewing UI component
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum


class LogLevel(Enum):
    """Log severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: str
    category: str
    message: str
    details: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class ActivityLogger:
    """
    Advanced activity logger with structured logging and analytics
    """
    
    def __init__(self, log_file: str = "testbuddy_activity.log", 
                 max_file_size_mb: int = 10,
                 enable_console: bool = False):
        """
        Initialize activity logger
        
        Args:
            log_file: Path to log file
            max_file_size_mb: Maximum log file size before rotation
            enable_console: Also print logs to console
        """
        self.log_file = Path(log_file)
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convert to bytes
        self.enable_console = enable_console
        self.current_session_id: Optional[str] = None
        
        # Create logger
        self.logger = logging.getLogger("TestBuddy")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler with rotation
        self._setup_file_handler()
        
        # Console handler (optional)
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_format = logging.Formatter('[%(levelname)s] %(message)s')
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)
        
        # Log buffer for UI display (last 100 entries)
        self.log_buffer: List[LogEntry] = []
        self.max_buffer_size = 100
        
        # Initialize
        self.info("APPLICATION", "TestBuddy Activity Logger initialized")
    
    def _setup_file_handler(self):
        """Setup file handler with custom formatting"""
        # Check if rotation needed
        if self.log_file.exists() and self.log_file.stat().st_size > self.max_file_size:
            self._rotate_log()
        
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Structured format
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
    
    def _rotate_log(self):
        """Rotate log file when size limit reached"""
        if not self.log_file.exists():
            return
        
        # Rename current log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = self.log_file.stem + f"_{timestamp}" + self.log_file.suffix
        backup_path = self.log_file.parent / backup_name
        
        self.log_file.rename(backup_path)
        self.info("SYSTEM", f"Log rotated to {backup_name}")
    
    def set_session(self, session_id: str):
        """Set current session ID for context"""
        self.current_session_id = session_id
        self.info("SESSION", f"Session set: {session_id}")
    
    def clear_session(self):
        """Clear current session context"""
        self.current_session_id = None
    
    def _log(self, level: LogLevel, category: str, message: str, 
             details: Optional[Dict[str, Any]] = None):
        """Internal logging method"""
        # Create log entry
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level.value,
            category=category,
            message=message,
            details=details,
            session_id=self.current_session_id
        )
        
        # Add to buffer
        self.log_buffer.append(entry)
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer.pop(0)
        
        # Format message for file logger
        log_msg = f"{category} | {message}"
        if details:
            detail_str = " | ".join([f"{k}={v}" for k, v in details.items()])
            log_msg += f" | {detail_str}"
        
        # Log to file
        if level == LogLevel.DEBUG:
            self.logger.debug(log_msg)
        elif level == LogLevel.INFO:
            self.logger.info(log_msg)
        elif level == LogLevel.WARNING:
            self.logger.warning(log_msg)
        elif level == LogLevel.ERROR:
            self.logger.error(log_msg)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(log_msg)
    
    # Convenience methods
    def debug(self, category: str, message: str, details: Optional[Dict] = None):
        """Log debug information"""
        self._log(LogLevel.DEBUG, category, message, details)
    
    def info(self, category: str, message: str, details: Optional[Dict] = None):
        """Log general information"""
        self._log(LogLevel.INFO, category, message, details)
    
    def warning(self, category: str, message: str, details: Optional[Dict] = None):
        """Log warning"""
        self._log(LogLevel.WARNING, category, message, details)
    
    def error(self, category: str, message: str, details: Optional[Dict] = None):
        """Log error"""
        self._log(LogLevel.ERROR, category, message, details)
    
    def critical(self, category: str, message: str, details: Optional[Dict] = None):
        """Log critical error"""
        self._log(LogLevel.CRITICAL, category, message, details)
    
    # Domain-specific logging helpers
    def log_ocr_start(self, image_size: tuple, language: str):
        """Log OCR processing start"""
        self.info("OCR", "OCR processing started", {
            "image_width": image_size[0],
            "image_height": image_size[1],
            "language": language
        })
    
    def log_ocr_complete(self, text_length: int, duration_ms: float):
        """Log OCR processing completion"""
        self.info("OCR", "OCR processing completed", {
            "text_length": text_length,
            "duration_ms": duration_ms
        })
    
    def log_ocr_error(self, error_message: str, error_type: str):
        """Log OCR processing error"""
        self.error("OCR", "OCR processing failed", {
            "error_type": error_type,
            "error_message": error_message
        })
    
    def log_session_created(self, session_id: str, session_name: str):
        """Log session creation"""
        self.info("SESSION", "Session created", {
            "session_id": session_id,
            "session_name": session_name
        })
    
    def log_session_saved(self, session_id: str, text_length: int):
        """Log session save"""
        self.info("SESSION", "Session saved", {
            "session_id": session_id,
            "text_length": text_length
        })
    
    def log_export(self, format: str, file_path: str, success: bool):
        """Log export operation"""
        if success:
            self.info("EXPORT", f"Export to {format} successful", {
                "format": format,
                "file_path": file_path
            })
        else:
            self.error("EXPORT", f"Export to {format} failed", {
                "format": format,
                "file_path": file_path
            })
    
    def log_ui_action(self, action: str, context: Optional[Dict] = None):
        """Log UI interaction"""
        self.debug("UI", f"User action: {action}", context)
    
    def get_recent_logs(self, count: int = 50, 
                       level: Optional[LogLevel] = None) -> List[LogEntry]:
        """
        Get recent log entries
        
        Args:
            count: Number of entries to return
            level: Filter by log level (None = all)
        
        Returns:
            List of recent log entries
        """
        logs = self.log_buffer[-count:]
        
        if level:
            logs = [log for log in logs if log.level == level.value]
        
        return logs
    
    def export_logs(self, output_path: Path, 
                   format: str = "json") -> bool:
        """
        Export logs to file
        
        Args:
            output_path: Path to output file
            format: Export format ("json", "txt", "csv")
        
        Returns:
            True if export successful
        """
        try:
            if format == "json":
                log_data = [entry.to_dict() for entry in self.log_buffer]
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(log_data, f, indent=2)
            
            elif format == "txt":
                with open(output_path, 'w', encoding='utf-8') as f:
                    for entry in self.log_buffer:
                        f.write(f"[{entry.timestamp}] [{entry.level}] {entry.category}: {entry.message}\n")
                        if entry.details:
                            for k, v in entry.details.items():
                                f.write(f"  {k}: {v}\n")
                        f.write("\n")
            
            elif format == "csv":
                import csv
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Level", "Category", "Message", "Details", "SessionID"])
                    for entry in self.log_buffer:
                        details_str = json.dumps(entry.details) if entry.details else ""
                        writer.writerow([
                            entry.timestamp,
                            entry.level,
                            entry.category,
                            entry.message,
                            details_str,
                            entry.session_id or ""
                        ])
            
            return True
        except Exception as e:
            self.error("LOGGER", f"Failed to export logs: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        level_counts = {}
        category_counts = {}
        
        for entry in self.log_buffer:
            level_counts[entry.level] = level_counts.get(entry.level, 0) + 1
            category_counts[entry.category] = category_counts.get(entry.category, 0) + 1
        
        return {
            "total_logs": len(self.log_buffer),
            "by_level": level_counts,
            "by_category": category_counts,
            "oldest_log": self.log_buffer[0].timestamp if self.log_buffer else None,
            "newest_log": self.log_buffer[-1].timestamp if self.log_buffer else None
        }


# Global logger instance
_global_logger: Optional[ActivityLogger] = None


def get_logger() -> ActivityLogger:
    """Get or create global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = ActivityLogger()
    return _global_logger


def set_logger(logger: ActivityLogger):
    """Set global logger instance"""
    global _global_logger
    _global_logger = logger
