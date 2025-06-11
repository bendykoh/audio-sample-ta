import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AllTranscriptionButton from './AllTranscriptionButton';
import api from '../api/axios';

// Mock the axios instance
vi.mock('../api/axios', () => ({
  default: {
    get: vi.fn()
  }
}));

describe('AllTranscriptionButton', () => {
  const mockTranscriptions = [
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

  it('renders the load button', () => {
    render(<AllTranscriptionButton />);
    expect(screen.getByRole('button', { name: /load all transcriptions/i })).toBeInTheDocument();
  });

  it('shows loading state when fetching transcriptions', async () => {
    // Mock a delayed response
    (api.get as any).mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({ data: mockTranscriptions }), 100)));

    render(<AllTranscriptionButton />);
    const button = screen.getByRole('button', { name: /load all transcriptions/i });

    await act(async () => {
      await userEvent.click(button);
    });

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('displays transcriptions when successfully loaded', async () => {
    (api.get as any).mockResolvedValueOnce({ data: mockTranscriptions });

    render(<AllTranscriptionButton />);
    const button = screen.getByRole('button', { name: /load all transcriptions/i });

    await act(async () => {
      await userEvent.click(button);
    });

    // Wait for transcriptions to be displayed
    expect(await screen.findByText('Loaded 2 transcription(s)')).toBeInTheDocument();
    expect(screen.getByText('Filename: test1.mp3')).toBeInTheDocument();
    expect(screen.getByText('Filename: test2.mp3')).toBeInTheDocument();
  });

  it('displays error message when fetch fails', async () => {
    const errorMessage = 'Failed to fetch transcriptions';
    (api.get as any).mockRejectedValueOnce(new Error(errorMessage));

    render(<AllTranscriptionButton />);
    const button = screen.getByRole('button', { name: /load all transcriptions/i });

    await act(async () => {
      await userEvent.click(button);
    });

    expect(await screen.findByText(`Error: ${errorMessage}`)).toBeInTheDocument();
  });

  it('calls onTranscriptionsLoaded callback when transcriptions are loaded', async () => {
    const onTranscriptionsLoaded = vi.fn();
    (api.get as any).mockResolvedValueOnce({ data: mockTranscriptions });

    render(<AllTranscriptionButton onTranscriptionsLoaded={onTranscriptionsLoaded} />);
    const button = screen.getByRole('button', { name: /load all transcriptions/i });

    await act(async () => {
      await userEvent.click(button);
    });

    expect(onTranscriptionsLoaded).toHaveBeenCalledWith(mockTranscriptions);
  });

  it('disables button while loading', async () => {
    // Mock a delayed response
    (api.get as any).mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({ data: mockTranscriptions }), 100)));

    render(<AllTranscriptionButton />);
    const button = screen.getByRole('button', { name: /load all transcriptions/i });

    await act(async () => {
      await userEvent.click(button);
    });

    expect(button).toBeDisabled();
  });
}); 