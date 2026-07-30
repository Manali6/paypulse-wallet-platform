import React, { useEffect } from 'react';
import { useWalletStore } from '../store/walletStore';
import { useAuthStore } from '../store/authStore';
import { formatCurrency, formatDate } from '../lib/formatters';
import { Wallet as WalletIcon, ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const { user } = useAuthStore();
  const { wallets, transactions, fetchWallets, fetchTransactions } = useWalletStore();

  useEffect(() => {
    fetchWallets();
    fetchTransactions({ page: 1, page_size: 5 });
  }, [fetchWallets, fetchTransactions]);

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Welcome back, {user?.display_name || 'User'}</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        {wallets.map((wallet) => (
          <div key={wallet.id} className="glass-card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontWeight: 600 }}>{wallet.currency} Wallet</span>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--bg-glass)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <WalletIcon size={16} color="var(--accent-primary)" />
              </div>
            </div>
            <div style={{ fontSize: '1.75rem', fontWeight: 700 }}>
              {formatCurrency(wallet.balance, wallet.currency)}
            </div>
          </div>
        ))}
      </div>

      <div className="glass-card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Recent Activity</h2>
          <Link to="/transactions" className="btn btn-secondary btn-sm">View All</Link>
        </div>

        {transactions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
            No transactions yet. Credit a wallet to get started!
          </div>
        ) : (
          <div className="animate-fade-in-up" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {transactions.map((tx) => (
              <div
                key={tx.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-glass)',
                  border: '1px solid var(--border)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      backgroundColor: tx.type === 'CREDIT' ? 'var(--success-bg)' : 'var(--danger-bg)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {tx.type === 'CREDIT' ? (
                      <ArrowDownLeft size={18} color="var(--success)" />
                    ) : (
                      <ArrowUpRight size={18} color="var(--danger)" />
                    )}
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9375rem' }}>{tx.description || tx.type}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{formatDate(tx.created_at)}</div>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div
                    style={{
                      fontWeight: 700,
                      color: tx.type === 'CREDIT' ? 'var(--success)' : 'var(--danger)',
                    }}
                  >
                    {tx.type === 'CREDIT' ? '+' : '-'}{formatCurrency(tx.amount, tx.currency)}
                  </div>
                  <span className={`badge ${tx.type === 'CREDIT' ? 'badge-credit' : 'badge-debit'}`}>
                    {tx.type}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
