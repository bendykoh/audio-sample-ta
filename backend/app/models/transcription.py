from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Transcription(Base):
    __tablename__ = "transcription"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    transcription_content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    