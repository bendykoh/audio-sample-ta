from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Transcription(Base):
    __tablename__ = "transcription"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    transcription_content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
