from __future__ import annotations

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import get_settings

settings = get_settings()

_s3_client = None


def _get_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    return _s3_client


def upload_file(file_bytes: bytes, s3_key: str, content_type: str = "application/octet-stream") -> str:
    """Upload bytes to S3. Returns the s3_key on success."""
    try:
        _get_client().put_object(
            Bucket=settings.S3_ATTACHMENT_BUCKET,
            Key=s3_key,
            Body=file_bytes,
            ContentType=content_type,
            ServerSideEncryption="aws:kms",
        )
        return s3_key
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"S3 upload failed for key '{s3_key}': {e}") from e


def download_file(s3_key: str) -> bytes:
    """Download a file from S3 and return its bytes."""
    try:
        response = _get_client().get_object(
            Bucket=settings.S3_ATTACHMENT_BUCKET,
            Key=s3_key,
        )
        return response["Body"].read()
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"S3 download failed for key '{s3_key}': {e}") from e


def delete_file(s3_key: str) -> None:
    """Delete an object from S3."""
    try:
        _get_client().delete_object(Bucket=settings.S3_ATTACHMENT_BUCKET, Key=s3_key)
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"S3 delete failed for key '{s3_key}': {e}") from e


def generate_presigned_url(s3_key: str, expiry_seconds: int = 900) -> str:
    """Generate a pre-signed GET URL valid for expiry_seconds (default 15 min)."""
    try:
        return _get_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_ATTACHMENT_BUCKET, "Key": s3_key},
            ExpiresIn=expiry_seconds,
        )
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"Failed to generate pre-signed URL for key '{s3_key}': {e}") from e
