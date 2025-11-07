"""
Storage Manager for handling file uploads
Supports multiple storage backends: S3, Local File System, and Database (Base64)
"""
import os
import base64
import boto3
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class StorageManager:
    """Unified storage manager supporting multiple backends"""
    
    def __init__(self):
        self.storage_type = os.getenv("STORAGE_TYPE", "local")  # local, s3, database
        
        # S3 Configuration
        self.s3_bucket = os.getenv("S3_BUCKET_NAME")
        self.s3_region = os.getenv("S3_REGION", "us-east-1")
        self.s3_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.s3_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        # Local storage configuration
        self.local_storage_path = os.getenv("LOCAL_STORAGE_PATH", "/app/uploads")
        
        # Initialize S3 client if configured
        if self.storage_type == "s3" and self.s3_access_key:
            self.s3_client = boto3.client(
                's3',
                region_name=self.s3_region,
                aws_access_key_id=self.s3_access_key,
                aws_secret_access_key=self.s3_secret_key
            )
        else:
            self.s3_client = None
    
    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        folder: str = "certificates",
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file using configured storage backend
        
        Args:
            file_content: File bytes
            filename: Original filename
            folder: Storage folder/prefix
            content_type: MIME type of file
            
        Returns:
            Dictionary with storage details
        """
        # Generate unique filename
        file_extension = filename.split('.')[-1] if '.' in filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
        
        try:
            if self.storage_type == "s3":
                return await self._upload_to_s3(file_content, unique_filename, folder, content_type)
            elif self.storage_type == "local":
                return await self._upload_to_local(file_content, unique_filename, folder)
            elif self.storage_type == "database":
                return await self._upload_to_database(file_content, unique_filename, content_type)
            else:
                raise ValueError(f"Unsupported storage type: {self.storage_type}")
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def _upload_to_s3(
        self,
        file_content: bytes,
        filename: str,
        folder: str,
        content_type: Optional[str]
    ) -> Dict[str, Any]:
        """Upload file to S3"""
        if not self.s3_client or not self.s3_bucket:
            raise ValueError("S3 not configured. Please set AWS credentials and bucket name.")
        
        key = f"{folder}/{filename}"
        
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        
        # Upload to S3
        self.s3_client.put_object(
            Bucket=self.s3_bucket,
            Key=key,
            Body=file_content,
            **extra_args
        )
        
        # Generate URL
        url = f"https://{self.s3_bucket}.s3.{self.s3_region}.amazonaws.com/{key}"
        
        return {
            "storage_type": "s3",
            "url": url,
            "bucket": self.s3_bucket,
            "key": key,
            "filename": filename,
            "uploaded_at": datetime.utcnow().isoformat()
        }
    
    async def _upload_to_local(
        self,
        file_content: bytes,
        filename: str,
        folder: str
    ) -> Dict[str, Any]:
        """Upload file to local file system"""
        # Create directory if it doesn't exist
        upload_dir = Path(self.local_storage_path) / folder
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / filename
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Generate relative URL
        url = f"/uploads/{folder}/{filename}"
        
        return {
            "storage_type": "local",
            "url": url,
            "path": str(file_path),
            "filename": filename,
            "uploaded_at": datetime.utcnow().isoformat()
        }
    
    async def _upload_to_database(
        self,
        file_content: bytes,
        filename: str,
        content_type: Optional[str]
    ) -> Dict[str, Any]:
        """Store file as base64 in database"""
        # Encode file to base64
        base64_content = base64.b64encode(file_content).decode('utf-8')
        
        # Create data URI
        data_uri = f"data:{content_type or 'application/octet-stream'};base64,{base64_content}"
        
        return {
            "storage_type": "database",
            "url": data_uri,
            "data": base64_content,
            "filename": filename,
            "content_type": content_type,
            "size": len(file_content),
            "uploaded_at": datetime.utcnow().isoformat()
        }
    
    async def delete_file(self, file_info: Dict[str, Any]) -> bool:
        """Delete file from storage"""
        try:
            storage_type = file_info.get("storage_type", self.storage_type)
            
            if storage_type == "s3":
                if self.s3_client and file_info.get("key"):
                    self.s3_client.delete_object(
                        Bucket=file_info.get("bucket", self.s3_bucket),
                        Key=file_info["key"]
                    )
                    return True
            
            elif storage_type == "local":
                if file_info.get("path"):
                    file_path = Path(file_info["path"])
                    if file_path.exists():
                        file_path.unlink()
                        return True
            
            elif storage_type == "database":
                # Nothing to delete from filesystem
                return True
            
            return False
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get current storage configuration"""
        return {
            "storage_type": self.storage_type,
            "local_path": self.local_storage_path if self.storage_type == "local" else None,
            "s3_bucket": self.s3_bucket if self.storage_type == "s3" else None,
            "s3_region": self.s3_region if self.storage_type == "s3" else None,
            "s3_configured": bool(self.s3_client) if self.storage_type == "s3" else False
        }


# Singleton instance
storage_manager = StorageManager()
