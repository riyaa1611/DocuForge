"""Tests for PDF generator service."""

import pytest

from app.services.pdf_generator import PDFGenerator


@pytest.mark.asyncio
async def test_generate_pdf():
    """Test PDF generation from HTML."""
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body>
        <h1>Test PDF</h1>
        <p>This is a test paragraph.</p>
    </body>
    </html>
    """
    
    try:
        pdf_bytes = await PDFGenerator.generate_pdf(html)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        # PDF magic bytes
        assert pdf_bytes[:4] == b'%PDF'
    finally:
        await PDFGenerator.close_browser()


@pytest.mark.asyncio
async def test_generate_pdf_with_options():
    """Test PDF generation with custom options."""
    html = "<html><body><h1>Test</h1></body></html>"
    
    try:
        pdf_bytes = await PDFGenerator.generate_pdf(
            html,
            format="Letter",
            margin={"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
        )
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
    finally:
        await PDFGenerator.close_browser()
