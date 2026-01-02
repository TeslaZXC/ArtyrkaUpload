from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import FileRecord
from schemas import FileRecordResponse
import os

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/files", response_model=List[FileRecordResponse])
async def list_files(db: Session = Depends(get_db)):
    files = db.query(FileRecord).all()
    for f in files:
        f.download_url = f"/{f.short_code}"
    return files

@router.delete("/files/{file_id}")
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(FileRecord).filter(FileRecord.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if os.path.exists(db_file.filepath):
        os.remove(db_file.filepath)
    
    db.delete(db_file)
    db.commit()
    
    return {"message": "File deleted successfully"}
