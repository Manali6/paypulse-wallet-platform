import React, { useEffect, useState } from 'react';
import { useWalletStore, type UserSearchResult } from '../store/walletStore';
import { formatCurrency, formatDate } from '../lib/formatters';
import { Send, Search, CheckCircle2, ArrowRight } from 'lucide-react';
import api from '../lib/api';
import { handleApiError } from '../lib/api';
import { Alert } from '../components/ui/Alert';

export const Transfers: React.FC = () => {
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const { wallets, transfers, fetchWallets, fetchTransfers, initiateTransfer } = useWalletStore();

  // Form State
  const [recipientEmail, setRecipientEmail] = useState('');
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Recipient Search State
  const [searchResults, setSearchResults] = useState<UserSearchResult[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    fetchWallets();
    fetchTransfers();
  }, [fetchWallets, fetchTransfers]);

  // Handle live recipient search with debouncing
  useEffect(() => {
    if (recipientEmail.trim().length < 2) {
      setSearchResults([]);
      setShowDropdown(false);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const response = await api.get(`/users/search?q=${encodeURIComponent(recipientEmail)}`);
        setSearchResults(response.data);
        setShowDropdown(true);
      } catch {
        setSearchResults([]);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [recipientEmail]);

  const handleSelectRecipient = (user: UserSearchResult) => {
    setRecipientEmail(user.email);
    setShowDropdown(false);
  };

  const handleTransferSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!recipientEmail || !amount || parseFloat(amount) <= 0) {
      setErrorMsg('Please enter a valid recipient and positive amount');
      setSuccessMsg(null);
      return;
    }

    // Generate unique idempotency key for this submission attempt
    const idempotencyKey = `idem-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setIsSubmitting(true);

    try {
      const transfer = await initiateTransfer({
        recipient_email: recipientEmail,
        amount,
        currency,
        idempotency_key: idempotencyKey,
        description,
      });

      setSuccessMsg(`Transferred ${formatCurrency(transfer.sent_amount, transfer.source_currency)} to ${recipientEmail}!`);
      setErrorMsg(null);
      setRecipientEmail('');
      setAmount('');
      setDescription('');
    } catch (err: any) {
      setErrorMsg(handleApiError(err, 'Transfer failed'));
      setSuccessMsg(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedWallet = wallets.find((w) => w.currency === currency) || wallets[0];

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Transfers</h1>
        <p>Send money to other PayPulse users across currencies with instant settlement</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '32px' }}>
        {/* Transfer Form Card */}
        <div className="glass-card" style={{ padding: '28px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Send size={20} color="var(--accent-primary)" />
            Send Money
          </h2>

          <form onSubmit={handleTransferSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {errorMsg && <Alert type="error" message={errorMsg} onClose={() => setErrorMsg(null)} />}
          {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}
            {/* Recipient Email with Search Dropdown */}
            <div className="input-group" style={{ position: 'relative' }}>
              <label>Recipient Email</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="email"
                  className="input"
                  value={recipientEmail}
                  onChange={(e) => setRecipientEmail(e.target.value)}
                  placeholder="recipient@example.com"
                  required
                />
                <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)' }} />
              </div>

              {/* Autocomplete Dropdown */}
              {showDropdown && searchResults.length > 0 && (
                <div
                  style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    right: 0,
                    backgroundColor: 'var(--bg-secondary)',
                    border: '1px solid var(--bg-glass-border)',
                    borderRadius: 'var(--radius-sm)',
                    boxShadow: 'var(--shadow-lg)',
                    zIndex: 200,
                    marginTop: '4px',
                    maxHeight: '200px',
                    overflowY: 'auto',
                  }}
                >
                  {searchResults.map((user) => (
                    <div
                      key={user.id}
                      onClick={() => handleSelectRecipient(user)}
                      style={{
                        padding: '10px 14px',
                        cursor: 'pointer',
                        borderBottom: '1px solid var(--border)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                      className="dropdown-item"
                    >
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{user.display_name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{user.email}</div>
                      </div>
                      <span className="badge badge-credit">{user.default_currency}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Source Wallet / Currency Selector */}
            <div className="input-group">
              <label>From Wallet</label>
              <select
                className="input"
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
              >
                {wallets.map((w) => (
                  <option key={w.id} value={w.currency} style={{ backgroundColor: 'var(--bg-secondary)' }}>
                    {w.currency} Wallet (Available: {formatCurrency(w.balance, w.currency)})
                  </option>
                ))}
              </select>
            </div>

            {/* Amount Input */}
            <div className="input-group">
              <label>Amount to Send</label>
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
              {selectedWallet && (
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Wallet Balance: {formatCurrency(selectedWallet.balance, selectedWallet.currency)}
                </div>
              )}
            </div>

            {/* Optional Note */}
            <div className="input-group">
              <label>Note / Description (Optional)</label>
              <input
                type="text"
                className="input"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g. Dinner split or Invoice #102"
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-lg"
              disabled={isSubmitting || !selectedWallet || parseFloat(selectedWallet.balance) <= 0}
              style={{ marginTop: '8px' }}
            >
              {isSubmitting ? 'Processing Transfer...' : 'Confirm Transfer'}
            </button>
          </form>
        </div>

        {/* Transfer History List */}
        <div className="glass-card" style={{ padding: '28px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '20px' }}>Transfer History</h2>

          {transfers.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
              No transfers yet. Send money to a friend above!
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '420px', overflowY: 'auto' }}>
              {transfers.map((t) => (
                <div
                  key={t.id}
                  style={{
                    padding: '14px 16px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-glass)',
                    border: '1px solid var(--border)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600, fontSize: '0.9375rem' }}>
                      <span>{formatCurrency(t.sent_amount, t.source_currency)}</span>
                      {t.source_currency !== t.target_currency && (
                        <>
                          <ArrowRight size={14} color="var(--text-muted)" />
                          <span>{formatCurrency(t.received_amount, t.target_currency)}</span>
                        </>
                      )}
                    </div>
                    <span className="badge badge-credit" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <CheckCircle2 size={12} />
                      {t.status}
                    </span>
                  </div>

                  <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                    {t.description || 'User-to-User Transfer'}
                  </div>

                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    {formatDate(t.created_at)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
