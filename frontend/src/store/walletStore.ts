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

export interface Transfer {
  id: string;
  sender_wallet_id: string;
  receiver_wallet_id: string;
  sent_amount: string;
  received_amount: string;
  source_currency: string;
  target_currency: string;
  exchange_rate: string;
  status: string;
  idempotency_key: string;
  description: string | null;
  created_at: string;
}

export interface ConversionRecord {
  id: string;
  from_wallet_id: string;
  to_wallet_id: string;
  from_amount: string;
  to_amount: string;
  from_currency: string;
  to_currency: string;
  rate_applied: string;
  idempotency_key: string;
  created_at: string;
}

export interface UserSearchResult {
  id: string;
  email: string;
  display_name: string;
  default_currency: string;
}

interface WalletState {
  wallets: Wallet[];
  transactions: Transaction[];
  transfers: Transfer[];
  conversions: ConversionRecord[];
  rates: Record<string, string>;
  totalTransactions: number;
  isLoading: boolean;

  fetchWallets: () => Promise<void>;
  createWallet: (currency: string) => Promise<void>;
  creditWallet: (walletId: string, amount: string, description?: string) => Promise<void>;
  debitWallet: (walletId: string, amount: string, description?: string) => Promise<void>;
  fetchTransactions: (params?: { wallet_id?: string; type?: string; page?: number; page_size?: number }) => Promise<void>;
  fetchTransfers: () => Promise<void>;
  initiateTransfer: (data: {
    recipient_email: string;
    amount: string;
    currency: string;
    idempotency_key: string;
    description?: string;
  }) => Promise<Transfer>;
  fetchRates: (base?: string) => Promise<void>;
  fetchConversions: () => Promise<void>;
  convertCurrency: (data: {
    from_currency: string;
    to_currency: string;
    amount: string;
    idempotency_key: string;
  }) => Promise<ConversionRecord>;
}

export const useWalletStore = create<WalletState>((set, get) => ({
  wallets: [],
  transactions: [],
  transfers: [],
  conversions: [],
  rates: {},
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

  fetchTransfers: async () => {
    set({ isLoading: true });
    try {
      const response = await api.get('/transfers');
      set({ transfers: response.data, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  initiateTransfer: async (data) => {
    const response = await api.post('/transfers', data);
    get().fetchWallets();
    get().fetchTransfers();
    return response.data;
  },

  fetchRates: async (base = 'USD') => {
    try {
      const response = await api.get(`/fx/rates?base=${base}`);
      set({ rates: response.data.rates });
    } catch {
      // Keep existing rates on error
    }
  },

  fetchConversions: async () => {
    set({ isLoading: true });
    try {
      const response = await api.get('/fx/conversions');
      set({ conversions: response.data, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  convertCurrency: async (data) => {
    const response = await api.post('/fx/convert', data);
    get().fetchWallets();
    get().fetchConversions();
    return response.data;
  },
}));
