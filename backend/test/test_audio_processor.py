import os
from io import BytesIO
from unittest.mock import Mock, patch

import pytest
from audio_processor.transcriber import AudioTranscriber


@pytest.fixture
def mock_transformers():
    with (
        patch("audio_processor.transcriber.WhisperProcessor") as mock_processor,  # noqa: E501
        patch(
            "audio_processor.transcriber.WhisperForConditionalGeneration"
        ) as mock_model,
    ):
        # Setup mock processor
        processor_instance = Mock()
        processor_instance.from_pretrained.return_value = processor_instance
        processor_instance.return_value = processor_instance
        processor_instance.batch_decode.return_value = ["This is a test transcription"]  # noqa: E501
        mock_processor.from_pretrained.return_value = processor_instance

        # Setup mock model
        model_instance = Mock()
        model_instance.from_pretrained.return_value = model_instance
        model_instance.generate.return_value = Mock()
        mock_model.from_pretrained.return_value = model_instance

        yield mock_processor, mock_model


@pytest.fixture
def sample_mp3():
    # Use the actual sample file from the test directory
    test_file_path = os.path.join(
        os.path.dirname(__file__), "object", "sample_test.mp3"
    )
    with open(test_file_path, "rb") as f:
        return BytesIO(f.read())


def test_audio_transcriber_initialization(mock_transformers):
    mock_processor, mock_model = mock_transformers
    transcriber = AudioTranscriber()
    assert transcriber is not None
    mock_processor.from_pretrained.assert_called_once_with("openai/whisper-tiny")  # noqa: E501
    mock_model.from_pretrained.assert_called_once_with("openai/whisper-tiny")


def test_process_audio_object(mock_transformers, sample_mp3):
    mock_processor, mock_model = mock_transformers
    transcriber = AudioTranscriber()
    result = transcriber.process_audio_object(sample_mp3)

    assert result == "This is a test transcription"
    mock_processor.from_pretrained.return_value.batch_decode.assert_called_once()  # noqa: E501


def test_process_audio_object_invalid_file():
    transcriber = AudioTranscriber()
    invalid_audio = BytesIO(b"not an audio file")

    result = transcriber.process_audio_object(invalid_audio)
    assert result is None


def test_process_audio_object_empty_file():
    transcriber = AudioTranscriber()
    empty_audio = BytesIO()

    result = transcriber.process_audio_object(empty_audio)
    assert result is None
