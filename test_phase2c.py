"""
Phase 2c Tests - Document Intelligence
=======================================

Tests for document intelligence features:
- Layout analysis
- Table detection
- Document classification
- Key field extraction
- Confidence scoring
"""

import unittest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from document_intelligence import (
    DocumentIntelligenceEngine,
    DocumentType,
    Word,
    TextLine,
    Table,
    DocumentLayout,
    ExtractedField,
    DocumentIntelligence,
    analyze_document,
    extract_field
)


class TestDocumentIntelligenceEngine(unittest.TestCase):
    """Test document intelligence engine"""

    def setUp(self):
        self.engine = DocumentIntelligenceEngine()

    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        self.assertIsNotNone(self.engine.doc_type_patterns)
        self.assertIsNotNone(self.engine.field_patterns)
        self.assertIn(DocumentType.INVOICE, self.engine.doc_type_patterns)

    def test_document_type_patterns_coverage(self):
        """Test all document types have patterns"""
        for doc_type in DocumentType:
            if doc_type != DocumentType.UNKNOWN:
                self.assertIn(doc_type, self.engine.doc_type_patterns)

    def test_field_pattern_coverage(self):
        """Test key field patterns exist"""
        expected_fields = [
            "invoice_number", "invoice_date", "due_date", "total_amount",
            "recipient", "sender", "phone", "email", "address", "zip_code"
        ]
        for field in expected_fields:
            self.assertIn(field, self.engine.field_patterns)


class TestDocumentClassification(unittest.TestCase):
    """Test document classification"""

    def setUp(self):
        self.engine = DocumentIntelligenceEngine()

    def test_classify_invoice(self):
        """Test invoice classification"""
        text = """
        INVOICE
        Invoice Number: INV-2025-001
        Invoice Date: 2025-01-15
        Bill To: John Doe
        Amount Due: $1,500.00
        """
        doc_type, confidence = self.engine._classify_document_type(text)
        self.assertEqual(doc_type, DocumentType.INVOICE)
        self.assertGreater(confidence, 0.3)

    def test_classify_receipt(self):
        """Test receipt classification"""
        text = """
        RECEIPT
        Receipt Number: RCP-12345
        Thank You for Your Purchase!
        Total Paid: $25.99
        Transaction ID: TXN-98765
        Item 1: Coffee - $5.00
        Item 2: Pastry - $3.50
        """
        doc_type, confidence = self.engine._classify_document_type(text)
        self.assertEqual(doc_type, DocumentType.RECEIPT)
        self.assertGreater(confidence, 0.3)

    def test_classify_contract(self):
        """Test contract classification"""
        text = """
        AGREEMENT
        This Agreement is entered into by and between the parties.
        Whereas the parties wish to establish terms and conditions,
        Now Therefore, it is agreed as follows.
        Signature: _________________________ Date: _________
        """
        doc_type, confidence = self.engine._classify_document_type(text)
        self.assertEqual(doc_type, DocumentType.CONTRACT)
        self.assertGreater(confidence, 0.2)

    def test_classify_form(self):
        """Test form classification"""
        text = """
        APPLICATION FORM
        Please complete all required fields below.
        Name: ___________________________
        Email: ___________________________
        Signature: _______________________ Date: _________
        """
        doc_type, confidence = self.engine._classify_document_type(text)
        self.assertEqual(doc_type, DocumentType.FORM)
        self.assertGreater(confidence, 0.2)

    def test_classify_unknown(self):
        """Test unknown document type"""
        text = "Random text with no structure"
        doc_type, confidence = self.engine._classify_document_type(text)
        self.assertEqual(doc_type, DocumentType.UNKNOWN)


class TestKeyFieldExtraction(unittest.TestCase):
    """Test key field extraction"""

    def setUp(self):
        self.engine = DocumentIntelligenceEngine()

    def test_extract_invoice_number(self):
        """Test invoice number extraction"""
        text = "Invoice Number: INV-2025-001"
        fields = self.engine._extract_key_fields(text, DocumentLayout())
        self.assertIn("invoice_number", fields)
        self.assertIn("2025-001", fields["invoice_number"].value)

    def test_extract_email(self):
        """Test email extraction"""
        text = "Contact: support@testbuddy.dev"
        fields = self.engine._extract_key_fields(text, DocumentLayout())
        self.assertIn("email", fields)
        self.assertEqual(fields["email"].value, "support@testbuddy.dev")

    def test_extract_phone(self):
        """Test phone number extraction"""
        text = "Phone: (555) 123-4567"
        fields = self.engine._extract_key_fields(text, DocumentLayout())
        self.assertIn("phone", fields)
        self.assertIn("555", fields["phone"].value)

    def test_extract_amount(self):
        """Test amount extraction"""
        text = "Total Amount Due: $1234.56"
        fields = self.engine._extract_key_fields(text, DocumentLayout())
        self.assertIn("total_amount", fields)
        self.assertIn("1234", fields["total_amount"].value)

    def test_extract_date(self):
        """Test date extraction"""
        text = "Invoice Date: 01/15/2025"
        fields = self.engine._extract_key_fields(text, DocumentLayout())
        self.assertIn("invoice_date", fields)

    def test_extract_multiple_fields(self):
        """Test extracting multiple fields at once"""
        text = """
        Invoice Number: INV-2025-001
        Invoice Date: 01/15/2025
        Amount Due: $1,500.00
        Phone: (555) 123-4567
        Email: customer@example.com
        """
        fields = self.engine._extract_key_fields(text, DocumentLayout())
        self.assertGreater(len(fields), 3)


class TestDataStructures(unittest.TestCase):
    """Test document intelligence data structures"""

    def test_word_creation(self):
        """Test Word dataclass"""
        word = Word(
            text="hello",
            confidence=0.95,
            bbox=(10, 20, 30, 40)
        )
        self.assertEqual(word.text, "hello")
        self.assertEqual(word.confidence, 0.95)
        self.assertEqual(word.bbox, (10, 20, 30, 40))

    def test_word_serialization(self):
        """Test Word serialization to dict"""
        word = Word("test", 0.9, (0, 0, 10, 10))
        d = word.to_dict()
        self.assertEqual(d["text"], "test")
        self.assertEqual(d["confidence"], 0.9)

    def test_textline_creation(self):
        """Test TextLine dataclass"""
        words = [Word("hello", 0.95, (0, 0, 20, 20))]
        line = TextLine(text="hello", words=words)
        self.assertEqual(line.text, "hello")
        self.assertEqual(len(line.words), 1)

    def test_textline_serialization(self):
        """Test TextLine serialization"""
        line = TextLine("test line")
        d = line.to_dict()
        self.assertIn("text", d)
        self.assertIn("words", d)

    def test_table_creation(self):
        """Test Table dataclass"""
        cells = [["A1", "B1"], ["A2", "B2"]]
        table = Table(
            rows=2,
            cols=2,
            cells=cells,
            bbox=(0, 0, 100, 100),
            confidence=0.85
        )
        self.assertEqual(table.rows, 2)
        self.assertEqual(table.cols, 2)
        self.assertEqual(table.confidence, 0.85)

    def test_extracted_field_creation(self):
        """Test ExtractedField dataclass"""
        field = ExtractedField(
            name="invoice_number",
            value="INV-2025-001",
            confidence=0.95,
            source="regex"
        )
        self.assertEqual(field.name, "invoice_number")
        self.assertEqual(field.value, "INV-2025-001")
        self.assertEqual(field.confidence, 0.95)

    def test_document_layout_creation(self):
        """Test DocumentLayout dataclass"""
        layout = DocumentLayout(
            page_width=1000,
            page_height=1500
        )
        self.assertEqual(layout.page_width, 1000)
        self.assertEqual(layout.page_height, 1500)
        self.assertEqual(len(layout.header), 0)
        self.assertEqual(len(layout.body), 0)

    def test_document_intelligence_serialization(self):
        """Test DocumentIntelligence serialization"""
        doc = DocumentIntelligence(
            file_path="test.pdf",
            doc_type=DocumentType.INVOICE,
            type_confidence=0.95,
            layout=DocumentLayout(),
            raw_text="Test content"
        )
        d = doc.to_dict()
        self.assertEqual(d["doc_type"], "invoice")
        self.assertEqual(d["file_path"], "test.pdf")
        self.assertEqual(d["type_confidence"], 0.95)

    def test_document_intelligence_json(self):
        """Test DocumentIntelligence JSON export"""
        doc = DocumentIntelligence(
            file_path="test.pdf",
            doc_type=DocumentType.INVOICE,
            type_confidence=0.95,
            layout=DocumentLayout()
        )
        json_str = doc.to_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed["doc_type"], "invoice")


class TestLayoutExtraction(unittest.TestCase):
    """Test layout extraction"""

    def setUp(self):
        self.engine = DocumentIntelligenceEngine()

    def test_layout_initialization(self):
        """Test DocumentLayout initializes correctly"""
        layout = DocumentLayout()
        self.assertEqual(len(layout.header), 0)
        self.assertEqual(len(layout.body), 0)
        self.assertEqual(len(layout.footer), 0)
        self.assertEqual(len(layout.tables), 0)

    def test_layout_serialization(self):
        """Test layout serialization"""
        layout = DocumentLayout(page_width=1000, page_height=1500)
        d = layout.to_dict()
        self.assertEqual(d["page_width"], 1000)
        self.assertEqual(d["page_height"], 1500)

    def test_finalize_text_line_header(self):
        """Test text line finalization in header"""
        layout = DocumentLayout(page_height=1500)
        bbox = (0, 50, 100, 20)  # In top third
        words = [Word("Header", 0.95, (0, 50, 100, 20))]
        self.engine._finalize_text_line(layout, "Header", words, bbox)
        self.assertEqual(len(layout.header), 1)

    def test_finalize_text_line_body(self):
        """Test text line finalization in body"""
        layout = DocumentLayout(page_height=1500)
        bbox = (0, 750, 100, 20)  # In middle
        words = [Word("Body", 0.95, (0, 750, 100, 20))]
        self.engine._finalize_text_line(layout, "Body", words, bbox)
        self.assertEqual(len(layout.body), 1)

    def test_finalize_text_line_footer(self):
        """Test text line finalization in footer"""
        layout = DocumentLayout(page_height=1500)
        bbox = (0, 1400, 100, 20)  # In bottom third
        words = [Word("Footer", 0.95, (0, 1400, 100, 20))]
        self.engine._finalize_text_line(layout, "Footer", words, bbox)
        self.assertEqual(len(layout.footer), 1)


class TestIntegrationFunctions(unittest.TestCase):
    """Test standalone integration functions"""

    def test_extract_field_function(self):
        """Test standalone extract_field function"""
        text = "Invoice Number: INV-2025-001"
        value = extract_field(text, "invoice_number")
        self.assertIsNotNone(value)
        self.assertIn("2025-001", value)

    def test_extract_field_not_found(self):
        """Test extract_field with non-existent field"""
        text = "Some random text"
        value = extract_field(text, "nonexistent_field")
        self.assertIsNone(value)


class TestDocumentProcessing(unittest.TestCase):
    """Test end-to-end document processing"""

    def setUp(self):
        self.engine = DocumentIntelligenceEngine()

    def test_raw_text_extraction(self):
        """Test raw text extraction from layout"""
        layout = DocumentLayout()
        layout.header.append(TextLine("Header"))
        layout.body.append(TextLine("Body"))
        layout.footer.append(TextLine("Footer"))

        text = self.engine._extract_raw_text(layout)
        self.assertIn("Header", text)
        self.assertIn("Body", text)
        self.assertIn("Footer", text)

    def test_confidence_scoring(self):
        """Test confidence scoring in word extraction"""
        word = Word("test", 0.95, (0, 0, 20, 20))
        self.assertGreaterEqual(word.confidence, 0.0)
        self.assertLessEqual(word.confidence, 1.0)


class TestErrorHandling(unittest.TestCase):
    """Test error handling"""

    def setUp(self):
        self.engine = DocumentIntelligenceEngine()

    def test_missing_file(self):
        """Test handling of missing file"""
        # Should not raise exception, but log warning
        result = self.engine.process_document("/nonexistent/path/file.pdf")
        self.assertIsNotNone(result)

    def test_invalid_patterns(self):
        """Test with invalid text patterns"""
        text = "!!@@##$$%%"
        doc_type, conf = self.engine._classify_document_type(text)
        # Should return UNKNOWN
        self.assertEqual(doc_type, DocumentType.UNKNOWN)


class TestDocumentTypes(unittest.TestCase):
    """Test DocumentType enum"""

    def test_all_document_types(self):
        """Test all document types are defined"""
        types = [t for t in DocumentType]
        self.assertIn(DocumentType.INVOICE, types)
        self.assertIn(DocumentType.RECEIPT, types)
        self.assertIn(DocumentType.CONTRACT, types)
        self.assertIn(DocumentType.FORM, types)
        self.assertIn(DocumentType.LETTER, types)
        self.assertIn(DocumentType.REPORT, types)
        self.assertIn(DocumentType.UNKNOWN, types)

    def test_document_type_values(self):
        """Test document type string values"""
        self.assertEqual(DocumentType.INVOICE.value, "invoice")
        self.assertEqual(DocumentType.RECEIPT.value, "receipt")
        self.assertEqual(DocumentType.UNKNOWN.value, "unknown")


def run_tests():
    """Run all Phase 2c tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentIntelligenceEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentClassification))
    suite.addTests(loader.loadTestsFromTestCase(TestKeyFieldExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestDataStructures))
    suite.addTests(loader.loadTestsFromTestCase(TestLayoutExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentTypes))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()
    exit(0 if result.wasSuccessful() else 1)
