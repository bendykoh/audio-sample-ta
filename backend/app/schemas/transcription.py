from datetime import datetime
from pydantic import BaseModel

class TranscriptionBase(BaseModel):
    filename: str
    transcription_content: str

class TranscriptionCreate(TranscriptionBase):
    pass

class TranscriptionResponse(TranscriptionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 