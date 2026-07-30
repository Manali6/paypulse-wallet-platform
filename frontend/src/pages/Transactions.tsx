import React, { useEffect, useState } from 'react';
import { useWalletStore } from '../store/walletStore';
import { formatCurrency, formatDate } from '../lib/formatters';
import { ArrowUpRight, ArrowDownLeft, Filter, ChevronLeft, ChevronRight } from 'lucide-react';

export const Transactions: React.FC = () => {
  const { wallets, transactions, totalTransactions, fetchWallets, fetchTransactions, isLoading } = useWalletStore();
  
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [walletFilter, setWalletFilter] = useState<string>('ALL');
  const [typeFilter, setTypeFilter] = useState<string>('ALL');

  useEffect(() => {
    fetchWallets();
  }, [fetchWallets]);

  useEffect(() => {
    const params: any = { page, page_size: pageSize };
    if (walletFilter !== 'ALL') params.wallet_id = walletFilter;
    if (typeFilter !== 'ALL') params.type = typeFilter;
    fetchTransactions(params);
  }, [page, pageSize, walletFilter, typeFilter, fetchTransactions]);

  const totalPages = Math.ceil(totalTransactions / pageSize);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  return (
    <div className="animate-in" style={{ paddingBottom: '40px' }}>
      <div className="page-header" style={{ marginBottom: '24px' }}>
        <h1>Transaction History</h1>
        <p>View and filter all your account activities</p>
      </div>

      <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={18} color="var(--text-secondary)" />
            <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Filters:</span>
          </div>

          <select 
            className="input" 
            style={{ width: 'auto', padding: '8px 12px', minWidth: '150px' }}
            value={walletFilter}
            onChange={(e) => {
              setWalletFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="ALL" style={{ backgroundColor: 'var(--bg-secondary)' }}>All Wallets</option>
            {wallets.map(w => (
              <option key={w.id} value={w.id} style={{ backgroundColor: 'var(--bg-secondary)' }}>
                {w.currency} Wallet
              </option>
            ))}
          </select>

          <select 
            className="input" 
            style={{ width: 'auto', padding: '8px 12px', minWidth: '150px' }}
            value={typeFilter}
            onChange={(e) => {
              setTypeFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="ALL" style={{ backgroundColor: 'var(--bg-secondary)' }}>All Types</option>
            <option value="CREDIT" style={{ backgroundColor: 'var(--bg-secondary)' }}>Credits (In)</option>
            <option value="DEBIT" style={{ backgroundColor: 'var(--bg-secondary)' }}>Debits (Out)</option>
          </select>
        </div>
      </div>

      <div className="glass-card" style={{ padding: '24px' }}>
        {isLoading && transactions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            Loading transactions...
          </div>
        ) : transactions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            No transactions found matching your filters.
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
                  padding: '16px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-glass)',
                  border: '1px solid var(--border)',
                  transition: 'transform var(--transition-fast), border-color var(--transition-fast)'
                }}
                onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--accent-primary)'}
                onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border)'}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div
                    style={{
                      width: '40px',
                      height: '40px',
                      borderRadius: '50%',
                      backgroundColor: tx.type === 'CREDIT' ? 'var(--success-bg)' : 'var(--danger-bg)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {tx.type === 'CREDIT' ? (
                      <ArrowDownLeft size={20} color="var(--success)" />
                    ) : (
                      <ArrowUpRight size={20} color="var(--danger)" />
                    )}
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '1rem', color: 'var(--text-primary)' }}>
                      {tx.description || tx.type}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                      {formatDate(tx.created_at)} • {tx.currency} Wallet
                    </div>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div
                    style={{
                      fontWeight: 700,
                      fontSize: '1.1rem',
                      color: tx.type === 'CREDIT' ? 'var(--success)' : 'var(--danger)',
                    }}
                  >
                    {tx.type === 'CREDIT' ? '+' : '-'}{formatCurrency(tx.amount, tx.currency)}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    Bal: {formatCurrency(tx.balance_after, tx.currency)}
                  </div>
                </div>
              </div>
            ))}

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: '24px', gap: '16px' }}>
                <button 
                  className="btn btn-secondary" 
                  style={{ padding: '8px 12px' }}
                  disabled={page === 1}
                  onClick={() => handlePageChange(page - 1)}
                >
                  <ChevronLeft size={18} />
                </button>
                
                <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Page {page} of {totalPages}
                </span>
                
                <button 
                  className="btn btn-secondary" 
                  style={{ padding: '8px 12px' }}
                  disabled={page === totalPages}
                  onClick={() => handlePageChange(page + 1)}
                >
                  <ChevronRight size={18} />
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
