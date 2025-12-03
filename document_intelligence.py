"""
Document Intelligence Module for TestBuddy
============================================

Provides OCR, layout analysis, table detection, document classification,
and key field extraction with confidence scoring.

Features:
- Layout analysis from OCR data
- Table detection and extraction
- Document type classification
- Key field extraction
- Confidence scoring per word/field
"""

import json
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from pathlib import Path
from datetime import datetime
import logging

try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    HAS_VISION = True
except ImportError:
    HAS_VISION = False

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Supported document types for classification"""
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    FORM = "form"
    LETTER = "letter"
    REPORT = "report"
    UNKNOWN = "unknown"


@dataclass
class Word:
    """Represents a single word with confidence score"""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    position: str = "unknown"  # "header", "body", "footer"

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TextLine:
    """Represents a line of text"""
    text: str
    words: List[Word] = field(default_factory=list)
    confidence: float = 0.0
    bbox: Tuple[int, int, int, int] = (0, 0, 0, 0)

    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "bbox": self.bbox,
            "words": [w.to_dict() for w in self.words]
        }


@dataclass
class Table:
    """Represents detected table"""
    rows: int
    cols: int
    cells: List[List[str]]
    bbox: Tuple[int, int, int, int]
    confidence: float

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DocumentLayout:
    """Represents document layout structure"""
    header: List[TextLine] = field(default_factory=list)
    body: List[TextLine] = field(default_factory=list)
    footer: List[TextLine] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    page_width: int = 0
    page_height: int = 0

    def to_dict(self) -> Dict:
        return {
            "header": [line.to_dict() for line in self.header],
            "body": [line.to_dict() for line in self.body],
            "footer": [line.to_dict() for line in self.footer],
            "tables": [table.to_dict() for table in self.tables],
            "page_width": self.page_width,
            "page_height": self.page_height
        }


@dataclass
class ExtractedField:
    """Represents extracted field with confidence"""
    name: str
    value: str
    confidence: float
    source: str = "unknown"  # "ocr", "layout", "regex"

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DocumentIntelligence:
    """Complete document intelligence result"""
    file_path: str
    doc_type: DocumentType
    type_confidence: float
    layout: DocumentLayout
    extracted_fields: Dict[str, ExtractedField] = field(default_factory=dict)
    raw_text: str = ""
    processing_time: float = 0.0
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "doc_type": self.doc_type.value,
            "type_confidence": self.type_confidence,
            "layout": self.layout.to_dict(),
            "extracted_fields": {k: v.to_dict() for k, v in self.extracted_fields.items()},
            "raw_text": self.raw_text,
            "processing_time": self.processing_time,
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(self.to_dict(), indent=2)


class DocumentIntelligenceEngine:
    """Main engine for document intelligence processing"""

    def __init__(self):
        self.vision_available = HAS_VISION
        self.logger = logging.getLogger(__name__)

        # Document type patterns
        self.doc_type_patterns = {
            DocumentType.INVOICE: [
                r"invoice\s*(?:number|no\.?|#)?",
                r"amount\s*due",
                r"invoice\s*date",
                r"bill\s*to",
                r"from|seller"
            ],
            DocumentType.RECEIPT: [
                r"receipt\s*(?:number|no\.?|#)?",
                r"total|amount.*paid",
                r"transaction\s*(?:id|number)",
                r"item.*(?:qty|quantity|price)",
                r"thank.*you"
            ],
            DocumentType.CONTRACT: [
                r"agreement|contract",
                r"party|parties",
                r"whereas",
                r"hereinafter",
                r"signature|signed",
                r"effective\s*date"
            ],
            DocumentType.FORM: [
                r"form\s*(?:number|no\.?|#)?",
                r"please.*(?:complete|fill)",
                r"required.*field|field.*required",
                r"\[.*\]|__+",  # Checkboxes or blank lines
                r"signature\s*(?:line|here)"
            ],
            DocumentType.LETTER: [
                r"(?:dear|to)\s+",
                r"sincerely|regards|respectfully",
                r"(?:mr\.|ms\.|dr\.)",
                r"address:|date:"
            ],
            DocumentType.REPORT: [
                r"report\s*(?:number|no\.?|#)?",
                r"annual|quarterly|monthly|executive\s*summary",
                r"table\s*of\s*contents",
                r"findings|conclusions",
                r"prepared\s*by|date"
            ]
        }

        # Key field patterns
        self.field_patterns = {
            "invoice_number": r"invoice\s*(?:number|no\.?|#)?\s*[:=]?\s*([A-Z0-9\-]+)",
            "invoice_date": r"invoice\s*date\s*[:=]?\s*([\d/\-\.]+)",
            "due_date": r"(?:due|payment)\s*date\s*[:=]?\s*([\d/\-\.]+)",
            "total_amount": r"(?:total|amount\s*due)\s*[:=]?\s*[^\d]*(\d+(?:[.,]\d+)*(?:[.,]\d{2})?)",
            "recipient": r"(?:to|bill\s*to|ship\s*to)\s*[:=]?\s*([A-Za-z\s]+)",
            "sender": r"(?:from|company|seller)\s*[:=]?\s*([A-Za-z\s]+)",
            "phone": r"(?:phone|tel)(?:ephone)?\s*[:=]?\s*([\d\-\(\)]+)",
            "email": r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})",
            "address": r"(?:address|street)\s*[:=]?\s*([0-9\s\w\.,#]+)",
            "zip_code": r"(?:zip|postal)\s*(?:code)?\s*[:=]?\s*(\d{5}(?:[-]?\d{4})?)"
        }

    def process_document(self, file_path: str) -> DocumentIntelligence:
        """
        Process a document and extract intelligence

        Args:
            file_path: Path to document file (image or PDF)

        Returns:
            DocumentIntelligence with all extracted data
        """
        import time
        start_time = time.time()

        file_path = str(file_path)
        logger.info(f"Processing document: {file_path}")

        # Step 1: Extract text and layout
        layout = self._extract_layout(file_path)
        raw_text = self._extract_raw_text(layout)

        # Step 2: Classify document type
        doc_type, type_confidence = self._classify_document_type(raw_text)

        # Step 3: Extract key fields
        extracted_fields = self._extract_key_fields(raw_text, layout)

        # Step 4: Detect tables
        self._detect_tables(file_path, layout)

        # Create result
        result = DocumentIntelligence(
            file_path=file_path,
            doc_type=doc_type,
            type_confidence=type_confidence,
            layout=layout,
            extracted_fields=extracted_fields,
            raw_text=raw_text,
            processing_time=time.time() - start_time,
            metadata={
                "vision_available": self.vision_available,
                "timestamp": datetime.now().isoformat()
            }
        )

        logger.info(f"Document processed: {doc_type.value} ({type_confidence:.2%} confidence)")
        return result

    def _extract_layout(self, file_path: str) -> DocumentLayout:
        """Extract document layout using OCR"""
        layout = DocumentLayout()

        if not self.vision_available:
            logger.warning("Vision libraries not available, using fallback mode")
            return layout

        try:
            # Load image
            img = Image.open(file_path)
            layout.page_width, layout.page_height = img.size

            # Extract text with Tesseract
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

            # Group text into lines
            current_line_y = -1
            current_line_text = ""
            current_line_words = []
            current_line_bbox = (0, 0, 0, 0)

            for i, word in enumerate(data['text']):
                if not word.strip():
                    continue

                y = data['top'][i]
                x = data['left'][i]
                w = data['width'][i]
                h = data['height'][i]
                conf = float(data['conf'][i]) / 100.0

                # Check if new line
                if abs(y - current_line_y) > 10 and current_line_text:
                    self._finalize_text_line(layout, current_line_text, current_line_words, current_line_bbox)
                    current_line_text = ""
                    current_line_words = []
                    current_line_y = y

                # Add word to current line
                current_line_y = y
                current_line_text += (" " if current_line_text else "") + word
                current_line_words.append(Word(word, conf, (x, y, w, h)))

                # Update line bbox
                if not current_line_bbox[2]:
                    current_line_bbox = (x, y, w, h)
                else:
                    current_line_bbox = (
                        min(current_line_bbox[0], x),
                        min(current_line_bbox[1], y),
                        max(current_line_bbox[2], x + w),
                        max(current_line_bbox[3], y + h)
                    )

            # Finalize last line
            if current_line_text:
                self._finalize_text_line(layout, current_line_text, current_line_words, current_line_bbox)

            logger.info(f"Extracted {len(layout.header) + len(layout.body) + len(layout.footer)} text lines")

        except Exception as e:
            logger.error(f"Error extracting layout: {e}")

        return layout

    def _finalize_text_line(self, layout: DocumentLayout, text: str, words: List[Word], bbox: Tuple):
        """Add completed text line to appropriate section"""
        # Determine position
        top_third = layout.page_height / 3
        bottom_third = layout.page_height * 2 / 3

        line = TextLine(
            text=text,
            words=words,
            confidence=sum(w.confidence for w in words) / len(words) if words else 0.0,
            bbox=bbox
        )

        if bbox[1] < top_third:
            layout.header.append(line)
        elif bbox[1] > bottom_third:
            layout.footer.append(line)
        else:
            layout.body.append(line)

    def _extract_raw_text(self, layout: DocumentLayout) -> str:
        """Extract all text from layout"""
        all_lines = layout.header + layout.body + layout.footer
        return "\n".join(line.text for line in all_lines)

    def _classify_document_type(self, text: str) -> Tuple[DocumentType, float]:
        """Classify document type based on content"""
        text_lower = text.lower()
        scores = {}

        for doc_type, patterns in self.doc_type_patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, text_lower, re.IGNORECASE))
            scores[doc_type] = matches / len(patterns)

        # Find best match
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]

        if confidence < 0.2:
            return DocumentType.UNKNOWN, confidence

        return best_type, confidence

    def _extract_key_fields(self, text: str, layout: DocumentLayout) -> Dict[str, ExtractedField]:
        """Extract key fields from document"""
        fields = {}
        text_lower = text.lower()

        for field_name, pattern in self.field_patterns.items():
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                value = match.group(1) if match.groups() else match.group(0)
                fields[field_name] = ExtractedField(
                    name=field_name,
                    value=value.strip(),
                    confidence=0.85,  # Regex-based extraction
                    source="regex"
                )

        return fields

    def _detect_tables(self, file_path: str, layout: DocumentLayout):
        """Detect and extract tables from document"""
        if not self.vision_available:
            return

        try:
            img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return

            # Detect lines
            edges = cv2.Canny(img, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=10)

            if lines is None:
                return

            # Simple table detection: count intersections
            h_lines = [l[0] for l in lines if abs(l[0][1] - l[0][3]) < 5]
            v_lines = [l[0] for l in lines if abs(l[0][0] - l[0][2]) < 5]

            if len(h_lines) > 2 and len(v_lines) > 2:
                table = Table(
                    rows=len(h_lines) - 1,
                    cols=len(v_lines) - 1,
                    cells=[["" for _ in range(len(v_lines) - 1)] for _ in range(len(h_lines) - 1)],
                    bbox=(0, 0, img.shape[1], img.shape[0]),
                    confidence=0.7
                )
                layout.tables.append(table)
                logger.info(f"Detected table: {table.rows}x{table.cols}")

        except Exception as e:
            logger.warning(f"Table detection failed: {e}")


class DocumentIntelligenceUI:
    """UI integration for document intelligence in TestBuddy"""

    def __init__(self, engine: DocumentIntelligenceEngine):
        self.engine = engine

    def create_intelligence_panel(self, parent):
        """Create UI panel for document intelligence features"""
        from PyQt6.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
            QLabel, QTextEdit, QComboBox, QProgressBar, QTableWidget,
            QTableWidgetItem, QTabWidget
        )
        from PyQt6.QtCore import Qt

        panel = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Document Intelligence")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Tabs for different features
        tabs = QTabWidget()

        # Tab 1: Document Analysis
        analysis_tab = self._create_analysis_tab()
        tabs.addTab(analysis_tab, "Analysis")

        # Tab 2: Extracted Fields
        fields_tab = self._create_fields_tab()
        tabs.addTab(fields_tab, "Fields")

        # Tab 3: Tables
        tables_tab = self._create_tables_tab()
        tabs.addTab(tables_tab, "Tables")

        layout.addWidget(tabs)

        # Action buttons
        button_layout = QHBoxLayout()
        process_btn = QPushButton("Analyze Document")
        process_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        button_layout.addWidget(process_btn)

        export_btn = QPushButton("Export Results")
        button_layout.addWidget(export_btn)

        layout.addLayout(button_layout)

        panel.setLayout(layout)
        return panel

    def _create_analysis_tab(self):
        """Create analysis tab"""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QProgressBar

        widget = QWidget()
        layout = QVBoxLayout()

        # Document type display
        type_label = QLabel("Document Type: UNKNOWN")
        type_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(type_label)

        # Confidence display
        confidence_label = QLabel("Confidence: 0%")
        layout.addWidget(confidence_label)

        # Progress
        progress = QProgressBar()
        progress.setValue(0)
        layout.addWidget(progress)

        # Raw text display
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlaceholderText("Document text will appear here...")
        layout.addWidget(text_edit)

        widget.setLayout(layout)
        return widget

    def _create_fields_tab(self):
        """Create extracted fields tab"""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel

        widget = QWidget()
        layout = QVBoxLayout()

        # Extracted fields table
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Field", "Value", "Confidence", "Source"])
        table.resizeColumnsToContents()
        layout.addWidget(table)

        # Summary
        summary = QLabel("No fields extracted yet")
        layout.addWidget(summary)

        widget.setLayout(layout)
        return widget

    def _create_tables_tab(self):
        """Create tables tab"""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem

        widget = QWidget()
        layout = QVBoxLayout()

        # Tables list
        tables_list = QTableWidget()
        tables_list.setColumnCount(3)
        tables_list.setHorizontalHeaderLabels(["Size", "Confidence", "Preview"])
        layout.addWidget(tables_list)

        # Info
        info = QLabel("Detected tables will appear here")
        layout.addWidget(info)

        widget.setLayout(layout)
        return widget


# Standalone functions for easy integration
def analyze_document(file_path: str) -> DocumentIntelligence:
    """Analyze a document and return intelligence results"""
    engine = DocumentIntelligenceEngine()
    return engine.process_document(file_path)


def extract_field(text: str, field_name: str) -> Optional[str]:
    """Extract a specific field from text"""
    engine = DocumentIntelligenceEngine()
    result = engine._extract_key_fields(text, DocumentLayout())
    return result.get(field_name).value if field_name in result else None


if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)

    print("Document Intelligence Module")
    print("============================")
    print(f"Vision libraries available: {HAS_VISION}")

    if not HAS_VISION:
        print("\nNote: Install vision libraries for full OCR support:")
        print("  pip install pytesseract pillow opencv-python numpy")
        print("  Also install Tesseract-OCR: https://github.com/UB-Mannheim/tesseract/wiki")
