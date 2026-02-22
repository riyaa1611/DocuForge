"""PDF generation service using Playwright."""

from typing import Optional
from loguru import logger
from playwright.async_api import async_playwright, Browser


class PDFGenerator:
    """
    Service for generating PDFs from HTML using Playwright.
    Uses Chromium headless browser for accurate rendering.
    """

    _browser: Optional[Browser] = None

    @classmethod
    async def get_browser(cls) -> Browser:
        """Get or create a shared browser instance."""
        if cls._browser is None or not cls._browser.is_connected():
            playwright = await async_playwright().start()
            cls._browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ],
            )
            logger.info("Playwright browser initialized")
        return cls._browser

    @classmethod
    async def close_browser(cls) -> None:
        """Close the browser instance."""
        if cls._browser is not None and cls._browser.is_connected():
            await cls._browser.close()
            cls._browser = None
            logger.info("Playwright browser closed")

    @classmethod
    async def generate_pdf(
        cls,
        html: str,
        format: str = "A4",
        print_background: bool = True,
        margin: Optional[dict] = None,
    ) -> bytes:
        """
        Generate a PDF from HTML content.

        Args:
            html: HTML content to convert to PDF
            format: Paper format (A4, Letter, etc.)
            print_background: Whether to print background graphics
            margin: Page margins (top, right, bottom, left)

        Returns:
            PDF file as bytes
        """
        browser = await cls.get_browser()
        page = await browser.new_page()

        try:
            # Set HTML content
            await page.set_content(html, wait_until="networkidle")

            # Generate PDF options
            pdf_options = {
                "format": format,
                "print_background": print_background,
            }

            if margin:
                pdf_options["margin"] = margin
            else:
                pdf_options["margin"] = {
                    "top": "20mm",
                    "right": "15mm",
                    "bottom": "20mm",
                    "left": "15mm",
                }

            # Generate PDF
            pdf_bytes = await page.pdf(**pdf_options)

            logger.debug(f"Generated PDF: {len(pdf_bytes)} bytes")
            return pdf_bytes

        finally:
            await page.close()

    @classmethod
    async def generate_pdf_from_url(
        cls,
        url: str,
        format: str = "A4",
        print_background: bool = True,
    ) -> bytes:
        """
        Generate a PDF from a URL.

        Args:
            url: URL to render
            format: Paper format
            print_background: Whether to print background graphics

        Returns:
            PDF file as bytes
        """
        browser = await cls.get_browser()
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="networkidle")

            pdf_bytes = await page.pdf(
                format=format,
                print_background=print_background,
                margin={
                    "top": "20mm",
                    "right": "15mm",
                    "bottom": "20mm",
                    "left": "15mm",
                },
            )

            return pdf_bytes

        finally:
            await page.close()
