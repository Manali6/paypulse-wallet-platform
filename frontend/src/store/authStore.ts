import { create } from 'zustand';
import api from '../lib/api';

interface User {
  id: string;
  email: string;
  display_name: string;
  default_currency: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, displayName: string, defaultCurrency: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,

  login: async (email, password) => {
    set({ isLoading: true });
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      set({ isAuthenticated: true });

      // Fetch user profile
      const userResponse = await api.get('/auth/me');
      set({ user: userResponse.data, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  signup: async (email, password, displayName, defaultCurrency) => {
    set({ isLoading: true });
    try {
      const response = await api.post('/auth/signup', {
        email,
        password,
        display_name: displayName,
        default_currency: defaultCurrency,
      });
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      set({ isAuthenticated: true });

      const userResponse = await api.get('/auth/me');
      set({ user: userResponse.data, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false });
  },

  fetchUser: async () => {
    try {
      const response = await api.get('/auth/me');
      set({ user: response.data, isAuthenticated: true });
    } catch {
      set({ user: null, isAuthenticated: false });
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  checkAuth: () => {
    const token = localStorage.getItem('access_token');
    set({ isAuthenticated: !!token });
  },
}));
