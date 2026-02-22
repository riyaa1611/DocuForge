"""Storage service for PDF file management."""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import aiofiles

from loguru import logger

from app.core.config import settings
from app.services.cloud_storage import CloudStorageService


class StorageService:
    """
    Service for managing PDF file storage.
    Delegates to CloudStorageService for actual storage operations.
    """
    
    @classmethod
    async def save_pdf(
        cls,
        pdf_bytes: bytes,
        filename: str,
        date: Optional[datetime] = None,
    ) -> tuple[str, int]:
        """
        Save a PDF file to configured storage backend.
        
        Args:
            pdf_bytes: PDF content as bytes
            filename: Name of the file
            date: Date for organizing the file (used for local storage)
            
        Returns:
            Tuple of (file path, file size)
        """
        # Use cloud storage service which handles all backends
        file_path, file_size = await CloudStorageService.save_file(
            file_data=pdf_bytes,
            filename=filename,
            content_type='application/pdf'
        )
        
        logger.info(f"Saved PDF: {file_path} ({file_size} bytes)")
        return file_path, file_size
    
    @classmethod
    async def get_pdf(cls, file_path: str) -> Optional[bytes]:
        """
        Retrieve a PDF file from storage.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            PDF content as bytes, or None if not found
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"PDF not found: {file_path}")
            return None
        
        async with aiofiles.open(path, "rb") as f:
            return await f.read()
    
    @classmethod
    def delete_pdf(cls, file_path: str) -> bool:
        """
        Delete a PDF file from storage.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted PDF: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete PDF {file_path}: {e}")
            return False
    
    @classmethod
    def cleanup_temp(cls, max_age_hours: int = 24) -> int:
        """
        Clean up old temporary files.
        
        Args:
            max_age_hours: Maximum age of temp files in hours
            
        Returns:
            Number of files deleted
        """
        temp_path = cls.get_temp_path()
        deleted = 0
        cutoff = datetime.now().timestamp() - (max_age_hours * 3600)
        
        try:
            for file in temp_path.iterdir():
                if file.is_file() and file.stat().st_mtime < cutoff:
                    file.unlink()
                    deleted += 1
            
            if deleted > 0:
                logger.info(f"Cleaned up {deleted} temp files")
            
            return deleted
        except Exception as e:
            logger.error(f"Temp cleanup error: {e}")
            return deleted
    
    @classmethod
    def get_file_info(cls, file_path: str) -> Optional[dict]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file info, or None if not found
        """
        path = Path(file_path)
        
        if not path.exists():
            return None
        
        stat = path.stat()
        return {
            "path": str(path),
            "name": path.name,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime),
            "modified": datetime.fromtimestamp(stat.st_mtime),
        }
