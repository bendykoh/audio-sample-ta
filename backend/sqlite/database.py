import os
import sqlite3
from pathlib import Path
from typing import List, Optional

"""Writer notes: 
This database creation is not used within the repo itself, but it is used to reset the database to the original state
This file should be run from `backend` directory using `python sqlite/database.py`.
The reason this was created is because initially I had issues trying to run whisper model with WSL2, it only worked better
when I used conda environment with pip to install torch and transformer package
"""


class AudioDatabaseHandler:
    def __init__(self, db_path: str = "transcription.db"):
        """Initialize database connection and create tables if they don't exist."""  # noqa: E501
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcription (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_filename TEXT,
                transcription_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def _read_transcription(self, audio_path: Path) -> Optional[str]:
        """Read transcription file content if it exists."""
        transcription_path = audio_path.parent / f"{audio_path.stem}_transcription.txt"  # noqa: E501
        if transcription_path.exists():
            with open(transcription_path, "r", encoding="utf-8") as f:
                content = f.read()
                return content
        return None

    def add_audio_file_transcription(self, filepath: str) -> bool:
        """
        Add an audio file transcription to the database.
        Returns True if successful, False if file already exists or error occurs.
        """  # noqa: E501
        try:
            file_path = Path(filepath)
            if not file_path.exists():
                print(f"File not found: {filepath}")
                return False

            if not file_path.suffix.lower() == ".mp3":
                print(f"Not an MP3 file: {filepath}")
                return False

            # Get transcription if available
            trans_content = self._read_transcription(file_path)

            self.cursor.execute(
                """
                INSERT INTO transcription (
                    filename,transcription_content
                )
                VALUES (?, ?)
            """,
                (file_path.name, trans_content),
            )

            self.conn.commit()
            return True

        except sqlite3.IntegrityError:
            print(f"File already exists in database: {filepath}")
            return False
        except Exception as e:
            print(f"Error adding file: {e}")
            return False

    def scan_directory(self, directory: str) -> int:
        """
        Scan the specified directory for MP3 files and add them to the database.
        Returns the number of files added.
        """  # noqa: E501
        directory_path = Path(directory)
        if not directory_path.exists():
            print(f"Directory not found: {directory}")
            return 0

        files_added = 0
        for file_path in directory_path.glob("*.mp3"):
            if self.add_audio_file_transcription(str(file_path)):
                files_added += 1
                print(f"Added: {file_path.name}")

        return files_added

    def get_all_files_info(self) -> List[tuple]:
        """Get all audio files from the database."""
        self.cursor.execute("SELECT * FROM transcription")
        return self.cursor.fetchall()

    def close(self):
        """Close the database connection."""
        self.conn.close()


def main():
    # Initialize database
    db = AudioDatabaseHandler()

    print(os.getcwd())
    directory = os.path.join(os.getcwd(), "data")

    # Scan data directory
    print("Scanning for audio files...")
    files_added = db.scan_directory(directory)
    print(f"\nAdded {files_added} audio files to the database")

    # Display all files
    print("\nFiles in database:")
    for file in db.get_all_files_info():
        print(f"- {file[1]}")
        if file[2]:  # if has transcription
            print(f"  Transcription: {file[2]}")

    db.close()


if __name__ == "__main__":
    main()
