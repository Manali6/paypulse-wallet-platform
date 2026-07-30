import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Alert } from './Alert';

describe('Alert Component', () => {
  it('renders success message correctly', () => {
    render(<Alert type="success" message="Transfer successful" />);
    expect(screen.getByText('Transfer successful')).toBeInTheDocument();
  });

  it('renders error message correctly', () => {
    render(<Alert type="error" message="Insufficient funds" />);
    expect(screen.getByText('Insufficient funds')).toBeInTheDocument();
  });

  it('does not render if message is empty', () => {
    const { container } = render(<Alert type="success" message="" />);
    expect(container.firstChild).toBeNull();
  });

  it('calls onClose when close button is clicked', () => {
    const handleClose = vi.fn();
    render(<Alert type="error" message="Error" onClose={handleClose} />);
    
    const closeButton = screen.getByRole('button');
    fireEvent.click(closeButton);
    
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
