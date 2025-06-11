import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from app.main import app
from app.models.transcription import Base
from app.db.database import get_db
from app.models.transcription import Transcription

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = testing_session()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_mp3():
    # Use the actual sample file from the test directory
    test_file_path = os.path.join(
        os.path.dirname(__file__), "object", "sample_test.mp3"
    )
    with open(test_file_path, "rb") as f:
        return f.read()


def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_transcriptions_empty(client):
    response = client.get("/api/v1/transcriptions")
    assert response.status_code == 200
    assert response.json() == []


def test_search_transcriptions_empty(client):
    response = client.get("/api/v1/search?query=test")
    assert response.status_code == 200
    assert response.json() == []


def test_upload_invalid_file(client):
    response = client.post(
        "/api/v1/transcribe",
        files={"audio_file": ("test.txt", b"not an audio file", "text/plain")},
    )
    assert response.status_code == 400
    assert "File must be an audio file" in response.json()["detail"]


def test_upload_valid_mp3(client, sample_mp3):
    response = client.post(
        "/api/v1/transcribe",
        files={"audio_file": ("test.mp3", sample_mp3, "audio/mpeg")},
    )
    assert response.status_code == 200
    assert "filename" in response.json()
    assert response.json()["filename"].endswith(".mp3")


def test_upload_mp3_with_same_filename(client, sample_mp3):
    # First upload
    response1 = client.post(
        "/api/v1/transcribe",
        files={"audio_file": ("test.mp3", sample_mp3, "audio/mpeg")},
    )
    assert response1.status_code == 200
    first_filename = response1.json()["filename"]

    # Second upload with same filename
    response2 = client.post(
        "/api/v1/transcribe",
        files={"audio_file": ("test.mp3", sample_mp3, "audio/mpeg")},
    )
    assert response2.status_code == 200
    second_filename = response2.json()["filename"]

    # Check that filenames are different
    assert first_filename != second_filename
    assert second_filename == "test_1.mp3"
