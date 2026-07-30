import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from './authStore';

describe('authStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
    });
    localStorage.clear();
  });

  it('checks auth status based on token', () => {
    // checkAuth only clears the state if the token is missing.
    useAuthStore.setState({ isAuthenticated: true, user: { id: '1' } as any });
    localStorage.removeItem('access_token');
    
    useAuthStore.getState().checkAuth();
    
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().user).toBeNull();
  });

  it('logs out and clears state', () => {
    const mockUser = { id: '1', email: 'test@example.com', display_name: 'Test', default_currency: 'USD', created_at: '2023-01-01' };
    useAuthStore.setState({ user: mockUser, isAuthenticated: true });
    localStorage.setItem('access_token', 'fake-token');

    useAuthStore.getState().logout();

    expect(useAuthStore.getState().user).toBeNull();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(localStorage.getItem('access_token')).toBeNull();
  });
});
