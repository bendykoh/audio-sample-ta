import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, act, waitFor } from '@testing-library/react';
import TranscriptionList from './TranscriptionList';
import api from '../api/axios';
import { url_params } from '../config';
import type { Transcription } from '../types';

// Mock the axios instance
vi.mock('../api/axios', () => ({
  default: {
    get: vi.fn()
  }
}));

describe('TranscriptionList', () => {
  const mockTranscriptions: Transcription[] = [
    {
      id: 1,
      filename: 'test1.mp3',
      transcription_content: 'Test transcription 1',
      created_at: '2024-03-10T10:00:00Z'
    },
    {
      id: 2,
      filename: 'test2.mp3',
      transcription_content: 'Test transcription 2',
      created_at: '2024-03-10T11:00:00Z'
    }
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders nothing initially when no search has been performed', () => {
    const { container } = render(<TranscriptionList searchQuery="" />);
    expect(container).toBeEmptyDOMElement();
  });

  it('shows error message when search query is empty', async () => {
    // First render with empty query - should show nothing
    const { rerender } = render(<TranscriptionList searchQuery="" />);
    expect(screen.queryByText('You need to add in a query.')).not.toBeInTheDocument();

    // Trigger a search with non-empty query to set hasSearched to true
    await act(async () => {
      rerender(<TranscriptionList searchQuery="test" />);
    });

    // Wait for the search to complete
    await waitFor(() => {
      expect(screen.queryByText('You need to add in a query.')).not.toBeInTheDocument();
    });

    // Now set empty query - should show error
    await act(async () => {
      rerender(<TranscriptionList searchQuery="" />);
    });

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText('You need to add in a query.')).toBeInTheDocument();
    });
  });

  it('shows loading state while fetching transcriptions', async () => {
    // Mock a delayed response
    vi.mocked(api.get).mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({ data: mockTranscriptions }), 100)));

    render(<TranscriptionList searchQuery="test" />);
    
    // Wait for loading state
    await waitFor(() => {
      expect(screen.getByText('Loading transcriptions...')).toBeInTheDocument();
    }, { timeout: 1000 });
  });

  it('displays transcriptions when search is successful', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockTranscriptions });

    render(<TranscriptionList searchQuery="test" />);

    // Wait for transcriptions to be displayed
    await waitFor(() => {
      expect(screen.getByText(/Filename: test1.mp3/)).toBeInTheDocument();
      expect(screen.getByText(/Filename: test2.mp3/)).toBeInTheDocument();
      expect(screen.getByText(/Test transcription 1/)).toBeInTheDocument();
      expect(screen.getByText(/Test transcription 2/)).toBeInTheDocument();
    }, { timeout: 1000 });
  });

  it('displays error message when search fails', async () => {
    const errorMessage = 'Failed to fetch transcriptions';
    
    // Clear any previous mocks and set up new mock
    vi.clearAllMocks();
    const mockError = new Error(errorMessage);
    
    // Add a small delay to ensure loading state is visible
    vi.mocked(api.get).mockImplementation(() => 
      new Promise((_, reject) => setTimeout(() => reject(mockError), 100))
    );

    render(<TranscriptionList searchQuery="test" />);

    // Wait for loading state
    await waitFor(() => {
      expect(screen.getByText('Loading transcriptions...')).toBeInTheDocument();
    });

    // Then wait for error message
    await waitFor(() => {
      expect(screen.queryByText('Loading transcriptions...')).not.toBeInTheDocument();
      const errorElement = screen.getByText(errorMessage);
      expect(errorElement).toBeInTheDocument();
      expect(errorElement).toHaveClass('text-red-500');
    });
  });

  it('makes API call with correct search query', async () => {
    const searchQuery = 'test query';
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockTranscriptions });

    render(<TranscriptionList searchQuery={searchQuery} />);

    // Wait for API call
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith(
        `${url_params.api.endpoints.search}?query=${encodeURIComponent(searchQuery)}`
      );
    }, { timeout: 1000 });
  });

  it('resets state when search query is cleared', async () => {
    const { rerender } = render(<TranscriptionList searchQuery="test" />);
    
    // First render with search query
    vi.mocked(api.get).mockResolvedValueOnce({ data: mockTranscriptions });
    
    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByText(/Filename: test1.mp3/)).toBeInTheDocument();
    }, { timeout: 1000 });

    // Clear search query
    await act(async () => {
      rerender(<TranscriptionList searchQuery="" />);
    });
    
    // Should show error message
    await waitFor(() => {
      expect(screen.getByText('You need to add in a query.')).toBeInTheDocument();
    }, { timeout: 1000 });
  });
}); 