"""
Modern Design System for TestBuddy
===================================

Apple-inspired design philosophy:
- Clean, minimal interface
- Generous whitespace
- Consistent typography
- Subtle animations
- Professional color palette
- Clear visual hierarchy
"""

from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt
from typing import Dict


class Colors:
    """
    Modern color palette inspired by Apple's design language
    """
    # Primary colors
    PRIMARY = "#007AFF"          # Apple Blue
    PRIMARY_HOVER = "#0051D5"
    PRIMARY_PRESSED = "#004BB8"
    
    # Neutral colors
    BACKGROUND = "#FFFFFF"
    BACKGROUND_SECONDARY = "#F5F5F7"
    BACKGROUND_TERTIARY = "#ECECEE"
    
    # Text colors
    TEXT_PRIMARY = "#1D1D1F"
    TEXT_SECONDARY = "#6E6E73"
    TEXT_TERTIARY = "#8E8E93"
    TEXT_ON_PRIMARY = "#FFFFFF"
    
    # Borders
    BORDER = "#D2D2D7"
    BORDER_LIGHT = "#E5E5EA"
    
    # Status colors
    SUCCESS = "#34C759"
    WARNING = "#FF9500"
    ERROR = "#FF3B30"
    INFO = "#5AC8FA"
    
    # Accent colors
    ACCENT_GREEN = "#30D158"
    ACCENT_ORANGE = "#FF9F0A"
    ACCENT_RED = "#FF453A"
    ACCENT_PURPLE = "#BF5AF2"
    
    # Dark mode (for future implementation)
    DARK_BACKGROUND = "#1C1C1E"
    DARK_SURFACE = "#2C2C2E"
    DARK_TEXT = "#FFFFFF"


class Typography:
    """
    Typography system following Apple's SF Pro font principles
    """
    # Font families (fallback to system fonts)
    FONT_FAMILY = "Segoe UI, -apple-system, BlinkMacSystemFont, sans-serif"
    FONT_FAMILY_MONO = "SF Mono, Consolas, Monaco, monospace"
    
    # Font sizes
    DISPLAY = 34
    TITLE_1 = 28
    TITLE_2 = 22
    TITLE_3 = 20
    HEADLINE = 17
    BODY = 15
    CALLOUT = 16
    SUBHEAD = 15
    FOOTNOTE = 13
    CAPTION_1 = 12
    CAPTION_2 = 11
    
    # Font weights
    LIGHT = 300
    REGULAR = 400
    MEDIUM = 500
    SEMIBOLD = 600
    BOLD = 700
    HEAVY = 800


class Spacing:
    """
    Spacing scale for consistent layout
    """
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32
    XXXXL = 48


class BorderRadius:
    """
    Border radius for rounded corners
    """
    SM = 4
    MD = 8
    LG = 12
    XL = 16
    FULL = 9999  # Fully rounded


class Shadows:
    """
    Shadow definitions for depth
    """
    SM = "0 1px 3px rgba(0, 0, 0, 0.12)"
    MD = "0 4px 6px rgba(0, 0, 0, 0.1)"
    LG = "0 10px 15px rgba(0, 0, 0, 0.1)"
    XL = "0 20px 25px rgba(0, 0, 0, 0.15)"


class ModernButton:
    """
    Button styles following Apple design
    """
    PRIMARY = f"""
        QPushButton {{
            background-color: {Colors.PRIMARY};
            color: {Colors.TEXT_ON_PRIMARY};
            border: none;
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.SM}px {Spacing.LG}px;
            font-size: {Typography.BODY}px;
            font-weight: {Typography.MEDIUM};
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {Colors.PRIMARY_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {Colors.PRIMARY_PRESSED};
        }}
        QPushButton:disabled {{
            background-color: {Colors.BACKGROUND_TERTIARY};
            color: {Colors.TEXT_TERTIARY};
        }}
    """
    
    SECONDARY = f"""
        QPushButton {{
            background-color: {Colors.BACKGROUND_SECONDARY};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER};
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.SM}px {Spacing.LG}px;
            font-size: {Typography.BODY}px;
            font-weight: {Typography.MEDIUM};
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {Colors.BACKGROUND_TERTIARY};
            border-color: {Colors.BORDER};
        }}
        QPushButton:pressed {{
            background-color: #D8D8D8;
        }}
        QPushButton:disabled {{
            background-color: {Colors.BACKGROUND_SECONDARY};
            color: {Colors.TEXT_TERTIARY};
        }}
    """
    
    ICON = f"""
        QPushButton {{
            background-color: transparent;
            color: {Colors.TEXT_PRIMARY};
            border: none;
            border-radius: {BorderRadius.SM}px;
            padding: {Spacing.SM}px;
            min-width: 36px;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {Colors.BACKGROUND_SECONDARY};
        }}
        QPushButton:pressed {{
            background-color: {Colors.BACKGROUND_TERTIARY};
        }}
    """


class ModernInput:
    """
    Input field styles
    """
    TEXT_EDIT = f"""
        QTextEdit {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_LIGHT};
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.MD}px;
            font-size: {Typography.BODY}px;
            selection-background-color: {Colors.PRIMARY};
            selection-color: {Colors.TEXT_ON_PRIMARY};
        }}
        QTextEdit:focus {{
            border: 2px solid {Colors.PRIMARY};
            padding: {Spacing.MD - 1}px;
        }}
    """
    
    LINE_EDIT = f"""
        QLineEdit {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_LIGHT};
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.SM}px {Spacing.MD}px;
            font-size: {Typography.BODY}px;
            min-height: 36px;
        }}
        QLineEdit:focus {{
            border: 2px solid {Colors.PRIMARY};
        }}
    """


class ModernList:
    """
    List widget styles
    """
    STYLE = f"""
        QListWidget {{
            background-color: {Colors.BACKGROUND};
            border: 1px solid {Colors.BORDER_LIGHT};
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.SM}px;
            outline: none;
        }}
        QListWidget::item {{
            background-color: transparent;
            color: {Colors.TEXT_PRIMARY};
            border-radius: {BorderRadius.SM}px;
            padding: {Spacing.MD}px;
            margin: {Spacing.XS}px 0;
            border: none;
        }}
        QListWidget::item:hover {{
            background-color: {Colors.BACKGROUND_SECONDARY};
        }}
        QListWidget::item:selected {{
            background-color: {Colors.PRIMARY};
            color: {Colors.TEXT_ON_PRIMARY};
        }}
        QListWidget::item:selected:!active {{
            background-color: {Colors.BACKGROUND_TERTIARY};
            color: {Colors.TEXT_PRIMARY};
        }}
    """


class ModernMenuBar:
    """
    Menu bar styles
    """
    STYLE = f"""
        QMenuBar {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT_PRIMARY};
            border-bottom: 1px solid {Colors.BORDER_LIGHT};
            padding: {Spacing.SM}px;
            font-size: {Typography.BODY}px;
        }}
        QMenuBar::item {{
            background-color: transparent;
            padding: {Spacing.SM}px {Spacing.MD}px;
            border-radius: {BorderRadius.SM}px;
        }}
        QMenuBar::item:selected {{
            background-color: {Colors.BACKGROUND_SECONDARY};
        }}
        QMenuBar::item:pressed {{
            background-color: {Colors.BACKGROUND_TERTIARY};
        }}
        
        QMenu {{
            background-color: {Colors.BACKGROUND};
            border: 1px solid {Colors.BORDER_LIGHT};
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.SM}px;
        }}
        QMenu::item {{
            background-color: transparent;
            color: {Colors.TEXT_PRIMARY};
            padding: {Spacing.SM}px {Spacing.XL}px;
            border-radius: {BorderRadius.SM}px;
        }}
        QMenu::item:selected {{
            background-color: {Colors.PRIMARY};
            color: {Colors.TEXT_ON_PRIMARY};
        }}
        QMenu::separator {{
            height: 1px;
            background-color: {Colors.BORDER_LIGHT};
            margin: {Spacing.SM}px 0;
        }}
    """


class ModernStatusBar:
    """
    Status bar styles
    """
    STYLE = f"""
        QStatusBar {{
            background-color: {Colors.BACKGROUND_SECONDARY};
            color: {Colors.TEXT_SECONDARY};
            border-top: 1px solid {Colors.BORDER_LIGHT};
            padding: {Spacing.SM}px;
            font-size: {Typography.FOOTNOTE}px;
        }}
    """


class ModernDialog:
    """
    Dialog styles
    """
    STYLE = f"""
        QDialog {{
            background-color: {Colors.BACKGROUND};
        }}
        QLabel {{
            color: {Colors.TEXT_PRIMARY};
            font-size: {Typography.BODY}px;
        }}
    """


def get_application_stylesheet() -> str:
    """
    Get complete application stylesheet
    """
    return f"""
        * {{
            font-family: {Typography.FONT_FAMILY};
        }}
        
        QMainWindow {{
            background-color: {Colors.BACKGROUND};
        }}
        
        QWidget {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT_PRIMARY};
        }}
        
        {ModernButton.PRIMARY}
        {ModernButton.SECONDARY}
        {ModernButton.ICON}
        {ModernInput.TEXT_EDIT}
        {ModernInput.LINE_EDIT}
        {ModernList.STYLE}
        {ModernMenuBar.STYLE}
        {ModernStatusBar.STYLE}
        {ModernDialog.STYLE}
        
        QSplitter::handle {{
            background-color: {Colors.BORDER_LIGHT};
            width: 1px;
            height: 1px;
        }}
        
        QScrollBar:vertical {{
            background: {Colors.BACKGROUND_SECONDARY};
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: {Colors.BORDER};
            border-radius: 6px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {Colors.TEXT_TERTIARY};
        }}
        
        QComboBox {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_LIGHT};
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.SM}px {Spacing.MD}px;
            min-height: 36px;
            font-size: {Typography.BODY}px;
        }}
        QComboBox:hover {{
            border-color: {Colors.BORDER};
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        
        QMessageBox {{
            background-color: {Colors.BACKGROUND};
        }}
        QMessageBox QLabel {{
            color: {Colors.TEXT_PRIMARY};
            font-size: {Typography.BODY}px;
        }}
    """


def create_font(size: int, weight: int = Typography.REGULAR) -> QFont:
    """Create a font with specified size and weight"""
    font = QFont()
    font.setPointSize(size)
    font.setWeight(weight)
    return font


# Icon mapping (text-based until proper icons are added)
class Icons:
    """Text-based icons (placeholder for future SVG/icon font)"""
    # Actions
    CAPTURE = "📷"  # Will replace with proper icon
    SAVE = "💾"
    EXPORT = "📤"
    UNDO = "↶"
    REDO = "↷"
    SEARCH = "🔍"
    
    # Navigation
    HOME = "⌂"
    BACK = "←"
    FORWARD = "→"
    CLOSE = "×"
    
    # Status
    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    
    # Formatting
    BOLD = "B"
    ITALIC = "I"
    UNDERLINE = "U"
    
    # Zoom
    ZOOM_IN = "+"
    ZOOM_OUT = "−"
    ZOOM_FIT = "⊡"
    
    # Other
    STAR = "★"
    STAR_OUTLINE = "☆"
    SETTINGS = "⚙"
    HELP = "?"
    MORE = "⋯"
