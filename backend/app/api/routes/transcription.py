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
    """
    Process and transcribe an uploaded audio file, storing the transcription in the database.

    This endpoint handles audio file upload, transcription, and storage. It includes duplicate
    filename handling by appending incremental numbers to filenames that already exist.

    Args:
        audio_file (UploadFile): The audio file to be transcribed. Must be an audio file format.
        db (Session): SQLAlchemy database session dependency injection.

    Returns:
        TranscriptionResponse: transcription object with all fields

    Raises:
        HTTPException:
            - 400: If the uploaded file is not an audio file
            - 500: If transcription fails or other server-side errors occur
    """  # noqa: E501
    # Check if file is an audio file
    # Frontend has already rejected all files except mp3 so this is just a sanity check
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
    """
    Retrieve all transcriptions from the database.

    This endpoint returns a list of all transcription records, including their IDs,
    filenames, transcribed content, and creation timestamps.

    Args:
        db (Session): SQLAlchemy database session dependency injection.

    Returns:
        List[TranscriptionResponse]: A list of transcription objects
    """  # noqa: E501
    transcriptions = db.query(Transcription).all()
    return transcriptions


@router.get("/search")
def search_transcriptions(query: str, db: Session = Depends(get_db)):
    """
    Search for transcriptions by filename using a case-insensitive partial match.

    This endpoint performs a fuzzy search on transcription filenames, returning all records
    where the filename contains the search query string (case-insensitive).

    Args:
        query (str): The search string to match against filenames
        db (Session): SQLAlchemy database session dependency injection.

    Returns:
        List[Transcription]: A list of matching transcription objects

    Example:
        A search query of "audio" will match filenames like "my_audio_1.mp3",
        "AUDIO_file_2.mp3", etc.
    """  # noqa: E501
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
