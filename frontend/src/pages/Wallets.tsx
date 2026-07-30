import React, { useEffect, useState } from 'react';
import { useWalletStore, type Wallet } from '../store/walletStore';
import { formatCurrency } from '../lib/formatters';
import { Plus, ArrowDownLeft, ArrowUpRight } from 'lucide-react';
import toast from 'react-hot-toast';
import { handleApiError } from '../lib/api';

const AVAILABLE_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'INR', 'CAD', 'AUD', 'CHF', 'CNY', 'SGD'];

export const Wallets: React.FC = () => {
  const { wallets, fetchWallets, createWallet, creditWallet, debitWallet } = useWalletStore();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [actionModal, setActionModal] = useState<{ type: 'credit' | 'debit'; wallet: Wallet } | null>(null);

  const [newCurrency, setNewCurrency] = useState('EUR');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const existingCurrencies = wallets.map((w) => w.currency);
  const selectableCurrencies = AVAILABLE_CURRENCIES.filter((c) => !existingCurrencies.includes(c));

  useEffect(() => {
    fetchWallets();
  }, [fetchWallets]);

  useEffect(() => {
    if (isAddModalOpen && selectableCurrencies.length > 0 && !selectableCurrencies.includes(newCurrency)) {
      setNewCurrency(selectableCurrencies[0]);
    }
  }, [isAddModalOpen, selectableCurrencies, newCurrency]);

  const handleCreateWallet = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await createWallet(newCurrency);
      toast.success(`${newCurrency} Wallet created!`);
      setIsAddModalOpen(false);
    } catch (err: any) {
      toast.error(handleApiError(err, 'Failed to create wallet'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!actionModal) return;
    setIsSubmitting(true);

    try {
      if (actionModal.type === 'credit') {
        await creditWallet(actionModal.wallet.id, amount, description);
        toast.success(`Credited ${formatCurrency(amount, actionModal.wallet.currency)}`);
      } else {
        await debitWallet(actionModal.wallet.id, amount, description);
        toast.success(`Debited ${formatCurrency(amount, actionModal.wallet.currency)}`);
      }
      setActionModal(null);
      setAmount('');
      setDescription('');
    } catch (err: any) {
      toast.error(handleApiError(err, 'Transaction failed'));
    } finally {
      setIsSubmitting(false);
    }
  };



  return (
    <div className="animate-in">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Wallets</h1>
          <p>Manage your balances across multiple currencies</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setIsAddModalOpen(true)}
          disabled={selectableCurrencies.length === 0}
        >
          <Plus size={18} />
          Add Wallet
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '24px' }}>
        {wallets.map((wallet) => (
          <div key={wallet.id} className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <span style={{ fontSize: '1.25rem', fontWeight: 800 }}>{wallet.currency}</span>
                <span className="badge badge-credit">Active</span>
              </div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.8125rem' }}>Current Balance</div>
              <div style={{ fontSize: '2rem', fontWeight: 700, margin: '4px 0 20px 0' }}>
                {formatCurrency(wallet.balance, wallet.currency)}
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                className="btn btn-secondary"
                style={{ flex: 1 }}
                onClick={() => setActionModal({ type: 'credit', wallet })}
              >
                <ArrowDownLeft size={16} color="var(--success)" />
                Credit
              </button>
              <button
                className="btn btn-secondary"
                style={{ flex: 1 }}
                onClick={() => setActionModal({ type: 'debit', wallet })}
              >
                <ArrowUpRight size={16} color="var(--danger)" />
                Debit
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Add Wallet Modal */}
      {isAddModalOpen && (
        <div className="modal-overlay" onClick={() => setIsAddModalOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Wallet</h2>
            <form onSubmit={handleCreateWallet}>
              <div className="input-group" style={{ marginBottom: '20px' }}>
                <label>Select Currency</label>
                <select
                  className="input"
                  value={newCurrency}
                  onChange={(e) => setNewCurrency(e.target.value)}
                >
                  {selectableCurrencies.map((c) => (
                    <option key={c} value={c} style={{ backgroundColor: 'var(--bg-secondary)' }}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setIsAddModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                  {isSubmitting ? 'Creating...' : 'Create Wallet'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Credit / Debit Action Modal */}
      {actionModal && (
        <div className="modal-overlay" onClick={() => setActionModal(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>
              {actionModal.type === 'credit' ? 'Credit' : 'Debit'} {actionModal.wallet.currency} Wallet
            </h2>
            <form onSubmit={handleTransaction}>
              <div className="input-group" style={{ marginBottom: '16px' }}>
                <label>Amount ({actionModal.wallet.currency})</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  className="input"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="0.00"
                  required
                />
              </div>

              <div className="input-group" style={{ marginBottom: '20px' }}>
                <label>Description (Optional)</label>
                <input
                  type="text"
                  className="input"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="e.g. Deposit or Withdrawal note"
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setActionModal(null)}>
                  Cancel
                </button>
                <button
                  type="submit"
                  className={`btn ${actionModal.type === 'credit' ? 'btn-primary' : 'btn-danger'}`}
                  disabled={isSubmitting}
                >
                  {isSubmitting
                    ? 'Processing...'
                    : actionModal.type === 'credit'
                    ? 'Confirm Credit'
                    : 'Confirm Debit'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
