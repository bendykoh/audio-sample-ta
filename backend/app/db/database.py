from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./transcription.db"  # Using relative path to current directory

# Note: check_same_thread is needed for SQLite to work with FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 