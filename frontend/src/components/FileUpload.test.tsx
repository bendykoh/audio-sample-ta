import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FileUpload from './FileUpload';
import api from '../api/axios';
import type { TranscriptionResponse } from '../types';

// Mock the axios instance
vi.mock('../api/axios', () => ({
  default: {
    post: vi.fn()
  }
}));

describe('FileUpload', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();
  });

  it('renders upload form elements', () => {
    render(<FileUpload />);
    
    expect(screen.getByText('Upload Audio Files')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /upload files/i })).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled(); // Button should be disabled initially
  });

  it('enables upload button when files are selected', async () => {
    render(<FileUpload />);
    
    const file = new File(['test audio content'], 'test.mp3', { type: 'audio/mpeg' });
    const input = screen.getByRole('button', { name: /upload files/i });
    
    // Initially disabled
    expect(input).toBeDisabled();
    
    // Select file
    const fileInput = screen.getByLabelText('Upload audio files');
    await act(async () => {
      await userEvent.upload(fileInput, file);
    });
    
    // Button should be enabled
    expect(input).not.toBeDisabled();
  });

  it('handles successful file upload', async () => {
    // Mock successful API response
    const mockResponse: { data: TranscriptionResponse } = {
      data: {
        id: 1,
        filename: 'saved_test.mp3',
        original_filename: 'test.mp3',
        transcription_content: 'Test transcription',
        created_at: new Date().toISOString()
      }
    };
    (api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce(mockResponse);

    render(<FileUpload />);
    
    // Select file
    const file = new File(['test audio content'], 'test.mp3', { type: 'audio/mpeg' });
    const fileInput = screen.getByLabelText('Upload audio files');
    await act(async () => {
      await userEvent.upload(fileInput, file);
    });
    
    // Click upload
    const uploadButton = screen.getByRole('button', { name: /upload files/i });
    await act(async () => {
      await userEvent.click(uploadButton);
    });
    
    // Wait for upload to complete
    await waitFor(() => {
      expect(screen.getByText('✓ test.mp3')).toBeInTheDocument();
    }, { timeout: 3000 });
    
    // Verify API was called correctly
    expect(api.post).toHaveBeenCalledWith(
      expect.any(String),
      expect.any(FormData),
      expect.objectContaining({
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    );
  });

  it('handles failed file upload', async () => {
    // Mock failed API response
    (api.post as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error('Upload failed'));

    render(<FileUpload />);
    
    // Select file
    const file = new File(['test audio content'], 'test.mp3', { type: 'audio/mpeg' });
    const fileInput = screen.getByLabelText('Upload audio files');
    await act(async () => {
      await userEvent.upload(fileInput, file);
    });
    
    // Click upload
    const uploadButton = screen.getByRole('button', { name: /upload files/i });
    await act(async () => {
      await userEvent.click(uploadButton);
    });
    
    // Wait for error to appear
    await waitFor(() => {
      expect(screen.getByText('✗ test.mp3')).toBeInTheDocument();
      expect(screen.getByText('Upload failed')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('rejects unsupported file types', async () => {
    render(<FileUpload />);
    
    // Select unsupported audio file (WAV instead of MP3)
    const file = new File(['test audio content'], 'test.wav', { type: 'audio/wav' });
    const fileInput = screen.getByLabelText('Upload audio files');
    await act(async () => {
      await userEvent.upload(fileInput, file);
    });
    
    // Click upload
    const uploadButton = screen.getByRole('button', { name: /upload files/i });
    await act(async () => {
      await userEvent.click(uploadButton);
    });
    
    // Wait for error to appear in upload results
    await waitFor(() => {
      const errorContainer = screen.getByText('✗ test.wav').closest('div');
      expect(errorContainer).toBeInTheDocument();
      expect(errorContainer).toHaveTextContent('Unsupported file type');
    }, { timeout: 3000 });
  });
}); 