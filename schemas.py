from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FileRecordBase(BaseModel):
    filename: str
    short_code: str
    download_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class FileRecordResponse(FileRecordBase):
    id: int
    content_type: str
    expires_at: Optional[datetime] = None

class FileUploadResponse(BaseModel):
    filename: str
    short_code: str
    download_url: str
