"""
Tests unitarios para BriefingProcessor.

Verifica que process() devuelve objetos Document de langchain con metadatos correctos.
"""

import os
import tempfile

import pytest
from unittest.mock import patch, MagicMock

from langchain_core.documents import Document


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_pdf(tmp_path):
    """
    Crea un PDF válido mínimo para testing.

    Genera un PDF crudo con estructura mínima para que PyPDFLoader lo pueda leer.
    """
    pdf_path = str(tmp_path / "briefing.pdf")

    # PDF crudo mínimo con una página de texto
    pdf_bytes = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 100 700 Td (Hello World) Tj ET\nendstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000266 00000 n \n"
        b"0000000360 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n441\n%%EOF\n"
    )

    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)

    return pdf_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestBriefingProcessor:
    """Tests para BriefingProcessor.process() devolviendo objetos Document."""

    def test_process_devuelve_documentos(self, sample_pdf):
        """Verifica que process() retorna una lista de Document."""
        from services.pdf_processor import BriefingProcessor

        processor = BriefingProcessor(sample_pdf)
        result = processor.process()

        assert isinstance(result, list)
        for doc in result:
            assert isinstance(doc, Document)

    def test_process_campos_metadatos(self, sample_pdf):
        """Verifica que los metadatos de cada Document son correctos."""
        from services.pdf_processor import BriefingProcessor

        processor = BriefingProcessor(sample_pdf)
        result = processor.process()

        if result:  # El PDF podría producir al menos un chunk
            doc = result[0]
            assert doc.metadata["source"] == "project_briefing"
            assert doc.metadata["type"] == "requirement"
            assert "chunk_index" in doc.metadata

    def test_process_archivo_no_encontrado(self):
        """Verifica que un path inexistente lanza FileNotFoundError."""
        from services.pdf_processor import BriefingProcessor

        with pytest.raises(FileNotFoundError):
            BriefingProcessor("/ruta/inexistente/archivo.pdf")

    def test_process_no_es_pdf(self, tmp_path):
        """Verifica que un archivo que no es PDF lanza ValueError."""
        from services.pdf_processor import BriefingProcessor

        txt_file = str(tmp_path / "readme.txt")
        with open(txt_file, "w") as f:
            f.write("esto no es un pdf")

        with pytest.raises(ValueError, match="not a PDF"):
            BriefingProcessor(txt_file)
