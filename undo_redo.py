"""
Undo/Redo System for TestBuddy Text Editor

Provides a comprehensive undo/redo system using PyQt6's QUndoStack.
Tracks all text changes and allows full history navigation.
"""

from __future__ import annotations

from typing import Optional, Union
from PyQt6.QtGui import QUndoStack, QUndoCommand
from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit


class TextEditCommand(QUndoCommand):
    """Represents a single text edit operation (insert, delete, replace)."""

    def __init__(self, editor: Union[QPlainTextEdit, QTextEdit], old_text: str, new_text: str, 
                 description: str = "Edit", command_id: int = -1) -> None:
        """Initialize text edit command.
        
        Args:
            editor: QPlainTextEdit or QTextEdit widget to modify
            old_text: Previous text content
            new_text: New text content
            description: Command description for UI display
            command_id: Unique ID for command merging
        """
        super().__init__(description)
        self.editor = editor
        self.old_text = old_text
        self.new_text = new_text
        self.command_id = command_id

    def id(self) -> int:
        """Return command ID for merging."""
        return self.command_id

    def mergeWith(self, other: QUndoCommand) -> bool:
        """Merge consecutive keystroke commands."""
        if other.id() != self.id():
            return False

        self.new_text = other.new_text
        return True

    def redo(self) -> None:
        """Apply the new text."""
        self.editor.blockSignals(True)
        if isinstance(self.editor, QPlainTextEdit):
            self.editor.setPlainText(self.new_text)
        else:
            self.editor.setHtml(self.new_text)
        self.editor.blockSignals(False)

    def undo(self) -> None:
        """Revert to old text."""
        self.editor.blockSignals(True)
        if isinstance(self.editor, QPlainTextEdit):
            self.editor.setPlainText(self.old_text)
        else:
            self.editor.setHtml(self.old_text)
        self.editor.blockSignals(False)


class UndoRedoManager:
    """Manages undo/redo operations for text editor."""

    def __init__(self, editor: Union[QPlainTextEdit, QTextEdit], max_stack_size: int = 100) -> None:
        """Initialize undo/redo manager.
        
        Args:
            editor: QPlainTextEdit or QTextEdit widget to manage
            max_stack_size: Maximum number of undo states to keep (default 100)
        """
        self.editor = editor
        self.undo_stack = QUndoStack()
        self.undo_stack.setUndoLimit(max_stack_size)
        self.last_saved_command_index = 0
        self.is_modified = False

    def push_command(self, command: TextEditCommand) -> None:
        """Push a text edit command onto the undo stack.
        
        Args:
            command: TextEditCommand to add to history
        """
        self.undo_stack.push(command)
        self.is_modified = True

    def text_changed(self, old_text: str, new_text: str, 
                    description: str = "Edit") -> None:
        """Record a text change.
        
        Args:
            old_text: Previous text content
            new_text: New text content
            description: Description of the change
        """
        command = TextEditCommand(self.editor, old_text, new_text, description, command_id=-1)
        self.push_command(command)

    def push_keystroke(self, old_text: str, new_text: str) -> None:
        """Record a keystroke, allowing merging."""
        command = TextEditCommand(self.editor, old_text, new_text, "Keystroke", command_id=1)
        self.push_command(command)

    def undo(self) -> None:
        """Undo the last action."""
        if self.can_undo():
            self.undo_stack.undo()

    def redo(self) -> None:
        """Redo the last undone action."""
        if self.can_redo():
            self.undo_stack.redo()

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self.undo_stack.canUndo()

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self.undo_stack.canRedo()

    def clear(self) -> None:
        """Clear undo/redo history."""
        self.undo_stack.clear()
        self.is_modified = False

    def mark_saved(self) -> None:
        """Mark current state as saved (no unsaved changes)."""
        self.last_saved_command_index = self.undo_stack.index()
        self.is_modified = False

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self.undo_stack.index() != self.last_saved_command_index or self.is_modified

    def get_undo_text(self) -> str:
        """Get description of next undo action."""
        return self.undo_stack.undoText() or "Undo"

    def get_redo_text(self) -> str:
        """Get description of next redo action."""
        return self.undo_stack.redoText() or "Redo"

    def get_history_count(self) -> int:
        """Get number of undo/redo steps available."""
        return self.undo_stack.count()

    def get_current_index(self) -> int:
        """Get current position in undo/redo history."""
        return self.undo_stack.index()
