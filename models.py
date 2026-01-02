from sqlalchemy import Column, Integer, String, DateTime
from database import Base
import datetime

class FileRecord(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    short_code = Column(String, unique=True, index=True)
    content_type = Column(String)
    filepath = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
