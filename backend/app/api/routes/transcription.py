from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from pydub import AudioSegment
import io
import soundfile as sf
import numpy as np

from app.db.database import get_db
from app.models.transcription import Transcription
from app.schemas.transcription import TranscriptionResponse
from audio_processor.transcriber import AudioTranscriber

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "healthy"}


@router.post("/transcribe", response_model=TranscriptionResponse)
async def create_transcription(
    audio_file: UploadFile = File(...), db: Session = Depends(get_db)
):
    # Check if file is an audio file
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file")

    try:
        # Initialize the transcriber
        transcriber = AudioTranscriber()

        # Read the uploaded file
        contents = await audio_file.read()
        audio_wav = io.BytesIO(contents)

        # Use process_audio_object to handle transcription
        text = transcriber.process_audio_object(audio_wav)

        if text is None:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio")

         # Handle duplicate filename
        original_filename = audio_file.filename
        final_filename = _get_unique_filename(db, original_filename)

        # Save to database
        db_transcription = Transcription(
            filename=final_filename, transcription_content=text
        )
        db.add(db_transcription)
        db.commit()
        db.refresh(db_transcription)

        return TranscriptionResponse(
            id=db_transcription.id,
            filename=db_transcription.filename,
            transcription_content=db_transcription.transcription_content,
            original_filename=original_filename,
            created_at=db_transcription.created_at,
        )   

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcriptions", response_model=List[TranscriptionResponse])
def get_transcriptions(db: Session = Depends(get_db)):
    transcriptions = db.query(Transcription).all()
    return transcriptions


@router.get("/search")
def search_transcriptions(query: str, db: Session = Depends(get_db)):
    transcriptions = (
        db.query(Transcription).filter(Transcription.filename.ilike(f"%{query}%")).all()
    )
    return transcriptions


def _get_unique_filename(db: Session, filename: str) -> str:
    """
    Helper function to generate a unique filename by appending _1, _2, etc. if the filename already exists
    """
    if not filename:
        return filename
    
    # Check if the original filename exists
    existing = db.query(Transcription).filter(Transcription.filename == filename).first()
    if not existing:
        return filename
    
    # Split filename and extension
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
        ext = '.' + ext
    else:
        name, ext = filename, ''
    
    # Find the highest number suffix
    counter = 1
    while True:
        new_filename = f"{name}_{counter}{ext}"
        existing = db.query(Transcription).filter(Transcription.filename == new_filename).first()
        if not existing:
            return new_filename
        counter += 1