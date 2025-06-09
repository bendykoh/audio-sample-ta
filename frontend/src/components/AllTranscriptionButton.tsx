
import { useState } from 'react';
import api from '../api/axios';
// import { url_params } from '../config';
import type { Transcription } from '../types';

interface TranscriptionsButtonProps {
    onTranscriptionsLoaded?: (transcriptions: Transcription[]) => void;
  }
  
const AllTranscriptionButton: React.FC<TranscriptionsButtonProps> = ({ 
    onTranscriptionsLoaded 
  }) => {
    const [transcriptions, setTranscriptions] = useState<Transcription[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
  
    const fetchTranscriptions = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await api.get('/transcriptions');
        const data = response.data;
        
        setTranscriptions(data);
        
        // Call the callback if provided
        if (onTranscriptionsLoaded) {
          onTranscriptionsLoaded(data);
        }
        
        console.log('Transcriptions loaded:', data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch transcriptions';
        setError(errorMessage);
        console.error('Error fetching transcriptions:', err);
      } finally {
        setLoading(false);
      }
    };
  
    return (
      <div className="mb-4">
        <button
          onClick={fetchTranscriptions}
          disabled={loading}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            loading
              ? 'bg-gray-400 cursor-not-allowed text-gray-200'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          {loading ? 'Loading...' : 'Load All Transcriptions'}
        </button>
        
        {error && (
          <div className="mt-2 text-red-600 text-sm">
            Error: {error}
          </div>
        )}
        
        {transcriptions.length > 0 && (
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-2">
              Loaded {transcriptions.length} transcription(s)
            </p>
            <div className="max-h-60 overflow-y-auto bg-gray-50 rounded-md p-3">
              {transcriptions.map((transcription) => (
                <div key={transcription.id} className="mb-2 p-2 bg-white rounded border">
                  <h3 className="font-medium text-sm">Filename: {transcription.filename}</h3>
                  <p className="text-sm mt-1 truncate">Transcription: {transcription.transcription_content}</p>
                  <p className="text-xs text-gray-500">Created: {new Date(transcription.created_at).toLocaleString()}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

export default AllTranscriptionButton;