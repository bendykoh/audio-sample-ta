import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import soundfile as sf
from scipy import signal

class AudioTranscriber:
    def __init__(self):
        self.processor = WhisperProcessor.from_pretrained("openai/whisper-tiny")
        self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")
        self.target_sampling_rate = 16000  # Whisper expects 16kHz audio
        
        if torch.cuda.is_available():
            self.model = self.model.to("cuda")
    
    def get_audio_info(self, file_path):
        """
        Get audio file information without loading the entire file
        Returns: sampling rate and number of channels
        """
        info = sf.info(file_path)
        return {
            'sampling_rate': info.samplerate,
            'channels': info.channels,
            'duration': info.duration,
            'format': info.format,
            'frames': info.frames
        }

    def resample_audio(self, audio_array, orig_sampling_rate):
        """
        Resample audio to 16kHz if necessary
        """
        if orig_sampling_rate != self.target_sampling_rate:
            # Calculate number of samples needed
            num_samples = int(len(audio_array) * float(self.target_sampling_rate) / orig_sampling_rate)
            # Resample audio
            audio_array = signal.resample(audio_array, num_samples)
        return audio_array

    def load_audio_from_file(self, file_path):
        """
        Load audio data from a local file
        Supports various audio formats (wav, mp3, etc.) depending on soundfile support
        """
        try:   
            # First get the audio info
            audio_info = self.get_audio_info(file_path)
            print(f"Audio file info:")
            print(f"- Sampling rate: {audio_info['sampling_rate']} Hz")
            print(f"- Channels: {audio_info['channels']}")
            print(f"- Duration: {audio_info['duration']:.2f} seconds")
            print(f"- Format: {audio_info['format']}")
            
            # Now load the audio data
            print(f"\nLoading audio from file: {file_path}")
            audio_array, sampling_rate = sf.read(file_path)
            
            # Resample only if necessary
            if sampling_rate != self.target_sampling_rate:
                print(f"Resampling from {sampling_rate}Hz to {self.target_sampling_rate}Hz...")
                audio_array = self.resample_audio(audio_array, sampling_rate)
                print("Resampling complete")
            else:
                print("Audio already at target sampling rate, no resampling needed")
            
            return audio_array
        except Exception as e:
            raise ValueError(f"Error loading audio file: {str(e)}")

    
    def transcribe(self, audio_array):
        """
        Transcribe audio using Whisper model
        """
        # Convert audio to mono if stereo
        if len(audio_array.shape) > 1:
            audio_array = audio_array.mean(axis=1)
        
        # Process the audio input
        input_features = self.processor(
            audio_array,
            sampling_rate=self.target_sampling_rate,
            return_tensors="pt"
        ).input_features
        
        if torch.cuda.is_available():
            input_features = input_features.to("cuda")
        
        print(f"Processing audio...")
        # Generate token ids
        predicted_ids = self.model.generate(input_features)
        
        # Decode the token ids to text
        transcription = self.processor.batch_decode(
            predicted_ids, 
            skip_special_tokens=True
        )[0]
        
        return transcription
    
    def process_audio_file(self, file_path):
        """
        Helper function to process a single audio file
        """   
        try:
            info = self.get_audio_info(file_path)
            print("\nAudio file information:")
            print(f"Path: {file_path}")
            print(f"Format: {info['format']}")
            print(f"Duration: {info['duration']:.2f} seconds")
            print(f"Sampling rate: {info['sampling_rate']} Hz")
            print(f"Channels: {info['channels']}")

            audio_array = self.load_audio_from_file(file_path)
            print("\nStarting transcription...")
            transcription = self.transcribe(audio_array)
            print("\nTranscription result:", transcription)
            return transcription.strip()
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return None

    def process_audio_object(self, audio_file):
        """
        Helper function to process an audio file object
        Args:
            audio_file: A file object containing audio data
        Returns:
            str: The transcription text or None if processing fails
        """   
        try:
            # Load audio data directly from the file object using soundfile
            audio_array, sampling_rate = sf.read(audio_file)
            
            print("\nAudio file loaded successfully")
            print(f"Sampling rate: {sampling_rate} Hz")
            print(f"Shape: {audio_array.shape}")
            
            # Resample audio to 16kHz if needed
            if sampling_rate != self.target_sampling_rate:
                print(f"\nResampling from {sampling_rate}Hz to {self.target_sampling_rate}Hz...")
                audio_array = self.resample_audio(audio_array, sampling_rate)
                print("Resampling complete")
            
            print("\nStarting transcription...")
            transcription = self.transcribe(audio_array)
            print("\nTranscription result:", transcription)
            return transcription.strip()
            
        except Exception as e:
            print(f"Error processing audio file object: {str(e)}")
            return None


# Example usage for file path
# I previously had some issues using wsl to process the files using whisper, 
# and it took a long time to process the files
if __name__ == "__main__":
    audio_files = ["data/Sample 1.mp3", "data/Sample 2.mp3", "data/Sample 3.mp3"]
    transcriber = AudioTranscriber()
    transcriptions = []
    for audio_file in audio_files:
        transcription = transcriber.process_audio_file(audio_file)
        transcriptions.append(transcription)
    print(transcriptions)

    # Save transcriptions to individual files
    for audio_file, transcription in zip(audio_files, transcriptions):
        if transcription:
            # Create output filename based on input filename
            output_filename = audio_file.replace('.mp3', '_transcription.txt')
            try:
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(transcription)
                print(f"Transcription saved to: {output_filename}")
            except Exception as e:
                print(f"Error saving transcription for {audio_file}: {str(e)}")
