import shutil
import os
import zipfile
import datetime
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models import FileRecord
from schemas import FileUploadResponse
from utils import generate_short_code

router = APIRouter()
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

def calculate_expiration(expiration: str) -> Optional[datetime.datetime]:
    now = datetime.datetime.utcnow()
    if expiration == "1d":
        return now + datetime.timedelta(days=1)
    elif expiration == "7d":
        return now + datetime.timedelta(days=7)
    elif expiration == "1m":
        return now + datetime.timedelta(days=30)
    elif expiration == "never":
        return None
    return None

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    files: List[UploadFile] = File(...), 
    expiration: str = Form("never"),
    db: Session = Depends(get_db)
):
    short_code = generate_short_code()
    while db.query(FileRecord).filter(FileRecord.short_code == short_code).first():
       short_code = generate_short_code()

    expires_at = calculate_expiration(expiration)
    
    if len(files) > 1:
        zip_filename = f"archive_{short_code}.zip"
        file_location = f"{UPLOAD_DIR}/{zip_filename}"
        
        with zipfile.ZipFile(file_location, 'w') as zipf:
            for file in files:
                file_content = await file.read()
                zipf.writestr(file.filename, file_content)
        
        final_filename = zip_filename
        content_type = "application/zip"
    else:
        file = files[0]
        final_filename = file.filename
        content_type = file.content_type
        if not content_type:
            content_type = "application/octet-stream"
            
        file_location = f"{UPLOAD_DIR}/{short_code}_{final_filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

    db_file = FileRecord(
        filename=final_filename,
        short_code=short_code,
        content_type=content_type,
        filepath=file_location,
        expires_at=expires_at
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {
        "filename": db_file.filename,
        "short_code": db_file.short_code,
        "download_url": f"/{db_file.short_code}"
    }

@router.get("/{short_code}")
async def get_file(short_code: str, db: Session = Depends(get_db)):
    db_file = db.query(FileRecord).filter(FileRecord.short_code == short_code).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if db_file.expires_at and db_file.expires_at < datetime.datetime.utcnow():
         raise HTTPException(status_code=404, detail="File expired")

    return FileResponse(db_file.filepath, filename=db_file.filename, media_type=db_file.content_type)
