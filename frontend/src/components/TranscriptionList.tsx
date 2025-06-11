import React, { useState } from 'react';
import type { Transcription } from '../types';
import { url_params } from '../config';
import api from '../api/axios';

interface Props {
  searchQuery: string;
}

const TranscriptionList: React.FC<Props> = ({ searchQuery }) => {
  const [transcriptions, setTranscriptions] = useState<Transcription[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  React.useEffect(() => {
    const fetchTranscriptions = async () => {
      // Handle empty search query
      if (searchQuery.trim() === '') {
        setError('You need to add in a query.');
        setTranscriptions([]);
        setHasSearched(true);
        return;
      }
      
      // fetch transcriptions with search query
      try {
        setLoading(true);
        setError(null);
        const url = `${url_params.api.endpoints.search}?query=${encodeURIComponent(searchQuery)}`;
        const { data } = await api.get(url);
        setTranscriptions(data);
        setHasSearched(true);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch transcriptions');
        setTranscriptions([]);
        setHasSearched(true);
      } finally {
        setLoading(false);
      }
    };

    // Only trigger search when searchQuery is not empty
    if (searchQuery && searchQuery.trim() !== '') {
      fetchTranscriptions();
    } else if (searchQuery === '' && hasSearched) {
      // Show error only if user has searched before and now cleared the input
      setError('You need to add in a query.');
      setTranscriptions([]);
      setLoading(false);
    } else if (searchQuery === '') {
      // Reset states when searchQuery is cleared initially
      setTranscriptions([]);
      setError(null);
      setHasSearched(false);
      setLoading(false);
    }
  }, [searchQuery, hasSearched]);

  if (!hasSearched && !error) return null;

  if (loading) {
    return <div className="p-4">Loading transcriptions...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }

  if (transcriptions.length === 0) {
    return <div className="p-4 text-gray-500">No matching transcriptions found.</div>;
  }

  return (
    <div className="space-y-4">
      {transcriptions.map((transcription) => (
        <div key={transcription.id} className="p-4 bg-white rounded-lg shadow">
          <h3 className="font-bold text-lg mb-2"> Filename: {transcription.filename}</h3>
          <p className="text-gray-600 mb-2">Transcription: {transcription.transcription_content}</p>
          <p className="text-sm text-gray-400">
            Created: {new Date(transcription.created_at).toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  );
};

export default TranscriptionList;