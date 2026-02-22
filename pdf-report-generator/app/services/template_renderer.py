"""Template rendering service using Jinja2."""

import base64
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger


class TemplateRenderer:
    """
    Service for rendering HTML templates using Jinja2.
    """
    
    _env: Optional[Environment] = None
    
    @classmethod
    def get_environment(cls) -> Environment:
        """Get or create the Jinja2 environment."""
        if cls._env is None:
            template_dir = Path(__file__).parent.parent / "templates"
            template_dir.mkdir(parents=True, exist_ok=True)
            
            cls._env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True,
            )
            
            # Add custom filters
            cls._env.filters['format_currency'] = cls.format_currency
            cls._env.filters['format_number'] = cls.format_number
            cls._env.filters['format_date'] = cls.format_date
            cls._env.filters['image_to_base64'] = cls.image_to_base64
            
            logger.info("Jinja2 environment initialized")
        
        return cls._env
    
    @classmethod
    def render_template(
        cls,
        template_name: str,
        context: dict[str, Any],
    ) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template file
            context: Template context variables
            
        Returns:
            Rendered HTML string
        """
        env = cls.get_environment()
        template = env.get_template(template_name)
        
        html = template.render(**context)
        logger.debug(f"Rendered template: {template_name}")
        
        return html
    
    @classmethod
    def render_string(cls, template_string: str, context: dict[str, Any]) -> str:
        """
        Render a template from a string.
        
        Args:
            template_string: Template as a string
            context: Template context variables
            
        Returns:
            Rendered HTML string
        """
        env = cls.get_environment()
        template = env.from_string(template_string)
        return template.render(**context)
    
    @staticmethod
    def format_currency(value: float, symbol: str = "$") -> str:
        """Format a number as currency."""
        return f"{symbol}{value:,.2f}"
    
    @staticmethod
    def format_number(value: float, decimals: int = 0) -> str:
        """Format a number with thousand separators."""
        return f"{value:,.{decimals}f}"
    
    @staticmethod
    def format_date(value: Any, format: str = "%B %d, %Y") -> str:
        """Format a date."""
        from datetime import datetime
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.strftime(format)
    
    @staticmethod
    def image_to_base64(image_path: str) -> str:
        """Convert an image file to base64 data URI."""
        try:
            with open(image_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            
            # Determine MIME type
            suffix = Path(image_path).suffix.lower()
            mime_types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".svg": "image/svg+xml",
            }
            mime = mime_types.get(suffix, "image/png")
            
            return f"data:{mime};base64,{data}"
        except Exception as e:
            logger.error(f"Failed to convert image to base64: {e}")
            return ""
