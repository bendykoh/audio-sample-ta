import pytest
from app.api.routes.transcription import _get_unique_filename
from app.models.transcription import Base, Transcription
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # noqa: E501


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_transcription(db_session):
    transcription = Transcription(
        filename="test.mp3",
        transcription_content="This is a test transcription",  # noqa: E501
    )
    db_session.add(transcription)
    db_session.commit()
    db_session.refresh(transcription)

    assert transcription.id is not None
    assert transcription.filename == "test.mp3"
    assert transcription.transcription_content == "This is a test transcription"  # noqa: E501


def test_get_transcription(db_session):
    # Create a transcription
    transcription = Transcription(
        filename="test.mp3",
        transcription_content="This is a test transcription",  # noqa: E501
    )
    db_session.add(transcription)
    db_session.commit()

    # Retrieve the transcription
    result = db_session.query(Transcription).filter_by(filename="test.mp3").first()  # noqa: E501
    assert result is not None
    assert result.transcription_content == "This is a test transcription"


def test_search_transcription(db_session):
    # Create multiple transcriptions
    transcriptions = [
        Transcription(filename="test1.mp3", transcription_content="First test"),  # noqa: E501
        Transcription(filename="test2.mp3", transcription_content="Second test"),  # noqa: E501
        Transcription(filename="other.mp3", transcription_content="Other content"),  # noqa: E501
    ]
    for t in transcriptions:
        db_session.add(t)
    db_session.commit()

    # Search for transcriptions
    results = (
        db_session.query(Transcription)
        .filter(Transcription.filename.ilike("%test%"))
        .all()
    )

    assert len(results) == 2
    assert any(t.filename == "test1.mp3" for t in results)
    assert any(t.filename == "test2.mp3" for t in results)


def test_duplicate_filename_handling(db_session):
    # Test the _get_unique_filename function directly
    filename = "test.mp3"

    # First call should return original filename
    result1 = _get_unique_filename(db_session, filename)
    assert result1 == filename

    # Create a transcription with the original filename
    transcription = Transcription(
        filename=filename, transcription_content="First transcription"  # noqa: E501
    )
    db_session.add(transcription)
    db_session.commit()

    # Second call should return modified filename
    result2 = _get_unique_filename(db_session, filename)
    assert result2 == "test_1.mp3"

    # Create another transcription with the modified filename
    transcription2 = Transcription(
        filename=result2, transcription_content="Second transcription"  # noqa: E501
    )
    db_session.add(transcription2)
    db_session.commit()

    # Third call should return another modified filename
    result3 = _get_unique_filename(db_session, filename)
    assert result3 == "test_2.mp3"
