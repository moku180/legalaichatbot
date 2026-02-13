import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
import os
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class S3Service:
    """Service for interacting with AWS S3"""
    
    def __init__(self):
        self.enabled = settings.USE_S3 and settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY
        if self.enabled:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket = settings.AWS_BUCKET_NAME
    
    async def upload_file(self, file_obj: UploadFile, object_name: str) -> bool:
        """Upload a file to S3 bucket"""
        if not self.enabled:
            return False
            
        try:
            # Reset file pointer
            file_obj.file.seek(0)
            self.s3_client.upload_fileobj(
                file_obj.file,
                self.bucket,
                object_name,
                ExtraArgs={'ContentType': file_obj.content_type}
            )
            logger.info(f"Uploaded {object_name} to bucket {self.bucket}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {e}")
            return False

    def upload_file_path(self, file_path: str, object_name: str) -> bool:
        """Upload a local file path to S3"""
        if not self.enabled:
            return False
            
        try:
            self.s3_client.upload_file(file_path, self.bucket, object_name)
            logger.info(f"Uploaded {file_path} to {object_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload file path to S3: {e}")
            return False

    def download_file(self, object_name: str, file_path: str) -> bool:
        """Download a file from S3 bucket"""
        if not self.enabled:
            return False
            
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self.s3_client.download_file(self.bucket, object_name, file_path)
            logger.info(f"Downloaded {object_name} to {file_path}")
            return True
        except ClientError as e:
            logger.error(f"Failed to download file from S3: {e}")
            return False

    def delete_file(self, object_name: str) -> bool:
        """Delete a file from S3 bucket"""
        if not self.enabled:
            return False
            
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=object_name)
            logger.info(f"Deleted {object_name} from bucket {self.bucket}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {e}")
            return False
            
    def file_exists(self, object_name: str) -> bool:
        """Check if file exists in S3"""
        if not self.enabled:
            return False
            
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=object_name)
            return True
        except ClientError:
            return False

# Global instance
s3_service = S3Service()
