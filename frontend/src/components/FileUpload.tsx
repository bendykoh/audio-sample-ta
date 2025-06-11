import React, { useState } from 'react';
import { url_params } from '../config';
import api from '../api/axios';
import type { TranscriptionResponse } from '../types';

interface UploadResult {
  originalFilename: string;
  savedFilename: string;
  success: boolean;
  error?: string;
}

const FileUpload: React.FC = () => {
  const [files, setFiles] = useState<FileList | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadResults, setUploadResults] = useState<UploadResult[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(e.target.files);
      setError(null);
      setUploadResults([]); // Clear previous results
    }
  };

  const handleUpload = async () => {
    if (!files || files.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setUploading(true);
    setError(null);
    setUploadResults([]);

    const results: UploadResult[] = [];

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const validTypes = ['audio/mpeg']; // Allow only mp3 files for now

        if (!validTypes.includes(file.type)) {
          results.push({
            originalFilename: file.name,
            savedFilename: file.name,
            success: false,
            error: `Unsupported file type`
          });
          continue; // Skip this file
        }

        try {
          const formData = new FormData();
          formData.append('audio_file', file);

          const response = await api.post<TranscriptionResponse>(url_params.api.endpoints.transcribe, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });

          // Extract the saved filename from the response
          const transcriptionData = response.data;
          const savedFilename = transcriptionData.filename;
          const originalFilename = transcriptionData.original_filename || file.name;

          results.push({
            originalFilename,
            savedFilename,
            success: true
          });

        } catch (fileError) {
          results.push({
            originalFilename: file.name,
            savedFilename: file.name,
            success: false,
            error: fileError instanceof Error ? fileError.message : 'Upload failed'
          });
        }
      }

      setUploadResults(results);

      // Clear the file input after processing all files
      setFiles(null);
      if (document.querySelector<HTMLInputElement>('input[type="file"]')) {
        document.querySelector<HTMLInputElement>('input[type="file"]')!.value = '';
      }

      // Set general error if all uploads failed
      const successfulUploads = results.filter(r => r.success);
      if (successfulUploads.length === 0) {
        setError('All uploads failed');
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload files');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Upload Audio Files</h2>
      <div className="flex flex-col gap-4">
        <input
          type="file"
          accept="audio/*"
          multiple
          onChange={handleFileChange}
          className="border p-2 rounded"
          disabled={uploading}
          aria-label="Upload audio files"
        />
        <button
          onClick={handleUpload}
          disabled={!files || uploading}
          className={`px-4 py-2 rounded ${
            uploading
              ? 'bg-gray-400'
              : 'bg-blue-500 hover:bg-blue-600 text-white'
          }`}
        >
          {uploading ? 'Uploading...' : 'Upload Files'}
        </button>
        
        {error && <p className="text-red-500">{error}</p>}
        
        {/* Upload Results */}
        {uploadResults.length > 0 && (
          <div className="mt-4">
            <h3 className="text-lg font-semibold mb-2">Upload Results:</h3>
            <div className="space-y-2">
              {uploadResults.map((result, index) => (
                <div
                  key={index}
                  className={`p-3 rounded border ${
                    result.success 
                      ? 'bg-green-50 border-green-200' 
                      : 'bg-red-50 border-red-200'
                  }`}
                >
                  {result.success ? (
                    <div className="text-green-800">
                      <p className="font-medium">✓ {result.originalFilename}</p>
                      {result.originalFilename !== result.savedFilename && (
                        <p className="text-sm">Saved as: {result.savedFilename}</p>
                      )}
                    </div>
                  ) : (
                    <div className="text-red-800">
                      <p className="font-medium">✗ {result.originalFilename}</p>
                      <p className="text-sm">{result.error}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;