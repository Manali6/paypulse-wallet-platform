import { create } from 'zustand';
import api from '../lib/api';

export interface Wallet {
  id: string;
  currency: string;
  balance: string;
  is_active: boolean;
  created_at: string;
}

export interface Transaction {
  id: string;
  wallet_id: string;
  type: string;
  amount: string;
  currency: string;
  balance_after: string;
  description: string | null;
  reference_id: string | null;
  created_at: string;
}

interface WalletState {
  wallets: Wallet[];
  transactions: Transaction[];
  totalTransactions: number;
  isLoading: boolean;

  fetchWallets: () => Promise<void>;
  createWallet: (currency: string) => Promise<void>;
  creditWallet: (walletId: string, amount: string, description?: string) => Promise<void>;
  debitWallet: (walletId: string, amount: string, description?: string) => Promise<void>;
  fetchTransactions: (params?: { wallet_id?: string; page?: number; page_size?: number }) => Promise<void>;
}

export const useWalletStore = create<WalletState>((set) => ({
  wallets: [],
  transactions: [],
  totalTransactions: 0,
  isLoading: false,

  fetchWallets: async () => {
    set({ isLoading: true });
    try {
      const response = await api.get('/wallets');
      set({ wallets: response.data, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  createWallet: async (currency) => {
    const response = await api.post('/wallets', { currency });
    set((state) => ({ wallets: [...state.wallets, response.data] }));
  },

  creditWallet: async (walletId, amount, description) => {
    await api.post(`/wallets/${walletId}/credit`, { amount, description });
    // Refresh wallets to get updated balance
    const response = await api.get('/wallets');
    set({ wallets: response.data });
  },

  debitWallet: async (walletId, amount, description) => {
    await api.post(`/wallets/${walletId}/debit`, { amount, description });
    const response = await api.get('/wallets');
    set({ wallets: response.data });
  },

  fetchTransactions: async (params = {}) => {
    set({ isLoading: true });
    try {
      const response = await api.get('/transactions', { params });
      set({
        transactions: response.data.transactions,
        totalTransactions: response.data.total,
        isLoading: false,
      });
    } catch {
      set({ isLoading: false });
    }
  },
}));
