import io
import os
from typing import List

from app.db.database import get_db
from app.models.transcription import Transcription
from app.schemas.transcription import TranscriptionResponse
from audio_processor.transcriber import AudioTranscriber
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

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
        raise HTTPException(status_code=400, detail="File must be an audio file")  # noqa: E501

    try:
        # Initialize the transcriber
        transcriber = AudioTranscriber()

        # Read the uploaded file
        contents = await audio_file.read()
        audio_wav = io.BytesIO(contents)

        # Use process_audio_object to handle transcription
        text = transcriber.process_audio_object(audio_wav)

        if text is None:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio")  # noqa: E501

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
        db.query(Transcription).filter(Transcription.filename.ilike(f"%{query}%")).all()  # noqa: E501
    )
    return transcriptions


def _get_unique_filename(db: Session, filename: str) -> str:
    """
    Helper function to generate a unique filename by appending _1, _2, etc. if the filename already exists
    """  # noqa: E501
    # Split the filename into base name and extension
    # For example: "audio.mp3" -> ("audio", ".mp3")
    name, ext = os.path.splitext(filename)

    # Get all filenames that start with the base name
    base_pattern = f"{name}_%{ext}"
    existing_files = (
        db.query(Transcription.filename)
        .filter(Transcription.filename.like(base_pattern))
        .all()
    )

    if not existing_files:
        return f"{name}_1{ext}"

    # Extract numbers from filenames and find max
    max_counter = 0
    for (filename,) in existing_files:
        try:
            # Extract number between last underscore and extension
            number = int(filename.rsplit("_", 1)[1].replace(ext, ""))
            max_counter = max(max_counter, number)
        except (ValueError, IndexError):
            continue

    return f"{name}_{max_counter + 1}{ext}"
