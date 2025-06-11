import { describe, it, expect, vi } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SearchBar from './SearchBar';

describe('SearchBar', () => {
  it('renders search input and button', () => {
    const mockOnSearch = vi.fn();
    render(<SearchBar onSearch={mockOnSearch} />);
    
    // Check if input and button are rendered
    expect(screen.getByPlaceholderText('Search transcriptions by filename...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
  });

  it('updates input value when typing', async () => {
    const mockOnSearch = vi.fn();
    render(<SearchBar onSearch={mockOnSearch} />);
    
    const input = screen.getByPlaceholderText('Search transcriptions by filename...');
    
    await act(async () => {
      await userEvent.type(input, 'test query');
    });
    
    expect(input).toHaveValue('test query');
  });

  it('calls onSearch with input value when form is submitted', async () => {
    const mockOnSearch = vi.fn();
    render(<SearchBar onSearch={mockOnSearch} />);
    
    const input = screen.getByPlaceholderText('Search transcriptions by filename...');
    const submitButton = screen.getByRole('button', { name: /search/i });
    
    // Type in the input
    await act(async () => {
      await userEvent.type(input, 'test query');
    });
    
    // Submit the form
    await act(async () => {
      await userEvent.click(submitButton);
    });
    
    // Check if onSearch was called with correct value
    expect(mockOnSearch).toHaveBeenCalledWith('test query');
  });

  it('prevents default form submission behavior', async () => {
    const mockOnSearch = vi.fn();
    const { container } = render(<SearchBar onSearch={mockOnSearch} />);
    
    // Get the form element
    const form = container.querySelector('form');
    if (!form) throw new Error('Form not found');

    // Create a spy on the form's submit event
    const submitSpy = vi.spyOn(form, 'submit');
    
    // Submit the form
    await act(async () => {
      await userEvent.click(screen.getByRole('button', { name: /search/i }));
    });
    
    // Check if the form's submit method was not called (prevented)
    expect(submitSpy).not.toHaveBeenCalled();
  });
}); 