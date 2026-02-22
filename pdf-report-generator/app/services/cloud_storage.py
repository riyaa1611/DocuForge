"""Cloud storage service supporting AWS S3 and MinIO."""

import os
import asyncio
from typing import Literal
from pathlib import Path
import aiofiles

try:
    import boto3
    from botocore.exceptions import ClientError

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from loguru import logger
from app.core.config import settings


StorageBackend = Literal["LOCAL", "S3", "MINIO"]


class CloudStorageService:
    """
    Unified storage service supporting local filesystem, AWS S3, and MinIO.

    Configured via environment variables:
    - STORAGE_BACKEND: LOCAL, S3, or MINIO
    - For S3: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, AWS_REGION
    - For MinIO: MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME
    """

    _s3_client = None
    _minio_client = None

    @classmethod
    def get_backend(cls) -> StorageBackend:
        """Get the configured storage backend."""
        return getattr(settings, "storage_backend", "LOCAL").upper()

    @classmethod
    def _get_s3_client(cls):
        """Get or create S3 client."""
        if cls._s3_client is None:
            if not BOTO3_AVAILABLE:
                raise ImportError(
                    "boto3 is required for S3 storage. Install with: pip install boto3"
                )

            cls._s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
            )
            logger.info("S3 client initialized")
        return cls._s3_client

    @classmethod
    def _get_minio_client(cls):
        """Get or create MinIO client."""
        if cls._minio_client is None:
            if not BOTO3_AVAILABLE:
                raise ImportError(
                    "boto3 is required for MinIO storage. Install with: pip install boto3"
                )

            cls._minio_client = boto3.client(
                "s3",
                endpoint_url=settings.minio_endpoint,
                aws_access_key_id=settings.minio_access_key,
                aws_secret_access_key=settings.minio_secret_key,
                region_name="us-east-1",  # MinIO doesn't care about region
                use_ssl=settings.minio_secure,
            )
            logger.info(f"MinIO client initialized: {settings.minio_endpoint}")
        return cls._minio_client

    @classmethod
    async def save_file(
        cls, file_data: bytes, filename: str, content_type: str = "application/pdf"
    ) -> tuple[str, int]:
        """
        Save file to configured storage backend.

        Args:
            file_data: File content as bytes
            filename: Desired filename
            content_type: MIME type

        Returns:
            Tuple of (file_path, file_size)
        """
        backend = cls.get_backend()
        file_size = len(file_data)

        if backend == "LOCAL":
            return await cls._save_local(file_data, filename), file_size
        elif backend == "S3":
            return await cls._save_s3(file_data, filename, content_type), file_size
        elif backend == "MINIO":
            return await cls._save_minio(file_data, filename, content_type), file_size
        else:
            raise ValueError(f"Unsupported storage backend: {backend}")

    @classmethod
    async def _save_local(cls, file_data: bytes, filename: str) -> str:
        """Save file to local filesystem."""
        # Create directory structure
        reports_dir = Path(settings.storage_path) / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        file_path = reports_dir / filename

        # Write file asynchronously
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_data)

        logger.info(f"Saved file locally: {file_path}")
        return str(file_path)

    @classmethod
    async def _save_s3(cls, file_data: bytes, filename: str, content_type: str) -> str:
        """Save file to AWS S3."""
        loop = asyncio.get_event_loop()
        client = cls._get_s3_client()
        bucket = settings.aws_s3_bucket_name
        key = f"reports/{filename}"

        def _upload():
            client.put_object(
                Bucket=bucket, Key=key, Body=file_data, ContentType=content_type
            )

        await loop.run_in_executor(None, _upload)

        file_url = f"s3://{bucket}/{key}"
        logger.info(f"Saved file to S3: {file_url}")
        return file_url

    @classmethod
    async def _save_minio(
        cls, file_data: bytes, filename: str, content_type: str
    ) -> str:
        """Save file to MinIO."""
        loop = asyncio.get_event_loop()
        client = cls._get_minio_client()
        bucket = settings.minio_bucket_name
        key = f"reports/{filename}"

        def _upload():
            # Create bucket if it doesn't exist
            try:
                client.head_bucket(Bucket=bucket)
            except ClientError:
                client.create_bucket(Bucket=bucket)
                logger.info(f"Created MinIO bucket: {bucket}")

            client.put_object(
                Bucket=bucket, Key=key, Body=file_data, ContentType=content_type
            )

        await loop.run_in_executor(None, _upload)

        file_url = f"minio://{bucket}/{key}"
        logger.info(f"Saved file to MinIO: {file_url}")
        return file_url

    @classmethod
    async def read_file(cls, file_path: str) -> bytes:
        """
        Read file from configured storage backend.

        Args:
            file_path: Path to file (local path or s3:// or minio:// URL)

        Returns:
            File content as bytes
        """
        if file_path.startswith("s3://"):
            return await cls._read_s3(file_path)
        elif file_path.startswith("minio://"):
            return await cls._read_minio(file_path)
        else:
            return await cls._read_local(file_path)

    @classmethod
    async def _read_local(cls, file_path: str) -> bytes:
        """Read file from local filesystem."""
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()

    @classmethod
    async def _read_s3(cls, file_url: str) -> bytes:
        """Read file from AWS S3."""
        loop = asyncio.get_event_loop()
        client = cls._get_s3_client()

        # Parse s3://bucket/key
        parts = file_url.replace("s3://", "").split("/", 1)
        bucket, key = parts[0], parts[1]

        def _download():
            response = client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()

        return await loop.run_in_executor(None, _download)

    @classmethod
    async def _read_minio(cls, file_url: str) -> bytes:
        """Read file from MinIO."""
        loop = asyncio.get_event_loop()
        client = cls._get_minio_client()

        # Parse minio://bucket/key
        parts = file_url.replace("minio://", "").split("/", 1)
        bucket, key = parts[0], parts[1]

        def _download():
            response = client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()

        return await loop.run_in_executor(None, _download)

    @classmethod
    async def delete_file(cls, file_path: str) -> None:
        """Delete file from storage."""
        if file_path.startswith("s3://"):
            await cls._delete_s3(file_path)
        elif file_path.startswith("minio://"):
            await cls._delete_minio(file_path)
        else:
            await cls._delete_local(file_path)

    @classmethod
    async def _delete_local(cls, file_path: str) -> None:
        """Delete file from local filesystem."""
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted local file: {file_path}")

    @classmethod
    async def _delete_s3(cls, file_url: str) -> None:
        """Delete file from AWS S3."""
        loop = asyncio.get_event_loop()
        client = cls._get_s3_client()

        parts = file_url.replace("s3://", "").split("/", 1)
        bucket, key = parts[0], parts[1]

        await loop.run_in_executor(
            None, lambda: client.delete_object(Bucket=bucket, Key=key)
        )
        logger.info(f"Deleted S3 file: {file_url}")

    @classmethod
    async def _delete_minio(cls, file_url: str) -> None:
        """Delete file from MinIO."""
        loop = asyncio.get_event_loop()
        client = cls._get_minio_client()

        parts = file_url.replace("minio://", "").split("/", 1)
        bucket, key = parts[0], parts[1]

        await loop.run_in_executor(
            None, lambda: client.delete_object(Bucket=bucket, Key=key)
        )
        logger.info(f"Deleted MinIO file: {file_url}")
