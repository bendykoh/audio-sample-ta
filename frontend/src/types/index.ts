export interface Transcription {
  id: number;
  filename: string;
  transcription_content: string;
  created_at: string;
}

export interface TranscriptionResponse {
  id: number;
  filename: string;
  original_filename: string;
  transcription_content: string;
  created_at: string;
} 