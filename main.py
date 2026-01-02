from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import files, admin
import asyncio
import datetime
from database import SessionLocal
from models import FileRecord
from fastapi.responses import FileResponse
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

if os.path.exists("frontend/dist/assets"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.get("/")
async def read_index():
    return FileResponse("frontend/dist/index.html")

app.include_router(admin.router)
app.include_router(files.router)

async def cleanup_expired_files():
    while True:
        db = SessionLocal()
        now = datetime.datetime.utcnow()
        expired_files = db.query(FileRecord).filter(FileRecord.expires_at < now).all()
        for file in expired_files:
            if os.path.exists(file.filepath):
                try:
                    os.remove(file.filepath)
                except Exception as e:
                    print(f"Error deleting file {file.filepath}: {e}")
            db.delete(file)
        db.commit()
        db.close()
        await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_expired_files())
