"""
Session history management for TestBuddy.
Stores OCR results with metadata in JSON format for persistence.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, asdict, field


@dataclass
class HistoryEntry:
    """A single OCR session entry."""
    timestamp: str
    text_length: int
    text_preview: str  # First 100 chars
    full_text: str
    language: str
    tags: List[str] = field(default_factory=list)
    is_favorite: bool = False  # Star/favorite flag
    created_at: str = ""  # ISO format datetime
    category: str = "General"  # Session category
    session_name: str = ""  # Session name (for display)
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class HistoryManager:
    """Manages persistent history of OCR sessions."""
    
    def __init__(self, history_file: str = "testbuddy_history.json", max_entries: int = 100):
        self.history_file = Path(history_file)
        self.max_entries = max_entries
        self.entries: List[HistoryEntry] = []
        self.load()
    
    def load(self) -> None:
        """Load history from JSON file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.entries = [
                        HistoryEntry(**entry) for entry in data
                    ]
            except Exception as e:
                print(f"Error loading history: {e}")
                self.entries = []
        else:
            self.entries = []
    
    def save(self) -> None:
        """Save history to JSON file."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump([asdict(entry) for entry in self.entries], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def add_entry(self, text: str, language: str = "eng", tags: Optional[List[str]] = None,
                  session_name: str = "", category: str = "General") -> None:
        """Add a new OCR result to history.
        
        Args:
            text: The OCR text content
            language: OCR language (default: eng)
            tags: List of tags for the session
            session_name: Name of the session
            category: Category of the document (General, Project, Receipt, Invoice)
        """
        if not text.strip():
            return
        
        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(),
            text_length=len(text),
            text_preview=text[:100],
            full_text=text,
            language=language,
            tags=tags or [],
            session_name=session_name,
            category=category,
            is_favorite=False,
            created_at=datetime.now().isoformat()
        )
        
        self.entries.insert(0, entry)  # Most recent first
        
        # Maintain max entries limit
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[:self.max_entries]
        
        self.save()
    
    def get_all(self) -> List[HistoryEntry]:
        """Return all history entries."""
        return self.entries
    
    def get_recent(self, count: int = 10) -> List[HistoryEntry]:
        """Return most recent N entries."""
        return self.entries[:count]
    
    def search(self, query: str) -> List[HistoryEntry]:
        """Search history by text content."""
        query_lower = query.lower()
        return [
            entry for entry in self.entries
            if query_lower in entry.full_text.lower()
        ]
    
    def clear(self) -> None:
        """Clear all history."""
        self.entries = []
        self.save()
    
    def delete_entry(self, index: int) -> None:
        """Delete a specific history entry by index."""
        if 0 <= index < len(self.entries):
            self.entries.pop(index)
            self.save()
    
    def toggle_favorite(self, index: int) -> bool:
        """Toggle favorite status for an entry.
        
        Args:
            index: Index of entry in history
            
        Returns:
            New favorite status
        """
        if 0 <= index < len(self.entries):
            self.entries[index].is_favorite = not self.entries[index].is_favorite
            self.save()
            return self.entries[index].is_favorite
        return False
    
    def get_favorites(self) -> list:
        """Get all favorite entries."""
        return [
            {
                "name": entry.session_name or f"Session {i}",
                "category": entry.category,
                "text_preview": entry.text_preview,
                "timestamp": entry.timestamp,
                "created_at": entry.created_at,
                "tags": entry.tags,
                "is_favorite": entry.is_favorite
            }
            for i, entry in enumerate(self.entries)
            if entry.is_favorite
        ]

    def get_summary(self) -> dict:
        """Get statistics about stored history."""
        if not self.entries:
            return {
                "total_entries": 0,
                "total_chars": 0,
                "avg_entry_length": 0
            }
        
        total_chars = sum(entry.text_length for entry in self.entries)
        return {
            "total_entries": len(self.entries),
            "total_chars": total_chars,
            "avg_entry_length": total_chars // len(self.entries)
        }
