import { describe, it, expect } from 'vitest';
import { render, screen} from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('renders main components and headings', () => {
    render(<App />);
    expect(screen.getByText('Audio Transcription App')).toBeInTheDocument();
    expect(screen.getByText('Search Transcriptions by name')).toBeInTheDocument();
    expect(screen.getByText('See all transcripts')).toBeInTheDocument();
  });
});