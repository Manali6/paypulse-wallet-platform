import React, { useEffect, useState } from 'react';
import { useWalletStore } from '../store/walletStore';
import { formatCurrency, formatDate } from '../lib/formatters';
import { RefreshCw, ArrowRightLeft, CheckCircle2, TrendingUp } from 'lucide-react';
import { handleApiError } from '../lib/api';
import { Alert } from '../components/ui/Alert';

const SUPPORTED_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'INR', 'CAD', 'AUD', 'CHF', 'CNY', 'SGD'];

export const Exchange: React.FC = () => {
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const { wallets, rates, conversions, fetchWallets, fetchRates, fetchConversions, convertCurrency } =
    useWalletStore();

  const [fromCurrency, setFromCurrency] = useState('USD');
  const [toCurrency, setToCurrency] = useState('EUR');
  const [amount, setAmount] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchWallets();
    fetchRates(fromCurrency);
    fetchConversions();
  }, [fetchWallets, fetchRates, fetchConversions, fromCurrency]);

  const sourceWallet = wallets.find((w) => w.currency === fromCurrency);

  // Calculate live conversion preview
  const rateVal = rates[toCurrency] ? parseFloat(rates[toCurrency]) : 1.0;
  const convertedPreview = amount && !isNaN(parseFloat(amount)) ? (parseFloat(amount) * rateVal).toFixed(2) : '0.00';

  const handleConvertSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (fromCurrency === toCurrency) {
      setErrorMsg('Source and target currencies must be different');
      setSuccessMsg(null);
      return;
    }

    if (!amount || parseFloat(amount) <= 0) {
      setErrorMsg('Please enter a positive amount to convert');
      setSuccessMsg(null);
      return;
    }

    if (!sourceWallet || parseFloat(sourceWallet.balance) < parseFloat(amount)) {
      setErrorMsg(`Insufficient ${fromCurrency} balance`);
      setSuccessMsg(null);
      return;
    }

    const idempotencyKey = `fx-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setIsSubmitting(true);

    try {
      const record = await convertCurrency({
        from_currency: fromCurrency,
        to_currency: toCurrency,
        amount,
        idempotency_key: idempotencyKey,
      });

      setSuccessMsg(`Successfully exchanged ${formatCurrency(record.from_amount, record.from_currency)} to ${formatCurrency(record.to_amount, record.to_currency)}`);
      setErrorMsg(null);
      setAmount('');
    } catch (err: any) {
      setErrorMsg(handleApiError(err, 'Conversion failed'));
      setSuccessMsg(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  const swapCurrencies = () => {
    const temp = fromCurrency;
    setFromCurrency(toCurrency);
    setToCurrency(temp);
  };

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Currency Exchange</h1>
        <p>Swap currencies instantly between your wallets using real-time automated FX rates</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '32px' }}>
        {/* Converter Card */}
        <div className="glass-card" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
              <ArrowRightLeft size={20} color="var(--accent-primary)" />
              Instant Swap
            </h2>
            <button
              onClick={() => fetchRates(fromCurrency)}
              className="btn btn-secondary"
              style={{ padding: '6px 12px', fontSize: '0.8125rem', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <RefreshCw size={14} /> Refresh Rates
            </button>
          </div>

          <form onSubmit={handleConvertSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {errorMsg && <Alert type="error" message={errorMsg} onClose={() => setErrorMsg(null)} />}
          {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}
            {/* From / To Currencies Row with Swap Button */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '12px', alignItems: 'flex-end' }}>
              <div className="input-group">
                <label>From Currency</label>
                <select className="input" value={fromCurrency} onChange={(e) => setFromCurrency(e.target.value)}>
                  {SUPPORTED_CURRENCIES.map((curr) => (
                    <option key={curr} value={curr} style={{ backgroundColor: 'var(--bg-secondary)' }}>
                      {curr}
                    </option>
                  ))}
                </select>
              </div>

              <button
                type="button"
                onClick={swapCurrencies}
                className="btn btn-secondary"
                style={{ height: '42px', padding: '0 12px', borderRadius: 'var(--radius-sm)' }}
                title="Swap Currencies"
              >
                <ArrowRightLeft size={16} />
              </button>

              <div className="input-group">
                <label>To Currency</label>
                <select className="input" value={toCurrency} onChange={(e) => setToCurrency(e.target.value)}>
                  {SUPPORTED_CURRENCIES.map((curr) => (
                    <option key={curr} value={curr} style={{ backgroundColor: 'var(--bg-secondary)' }}>
                      {curr}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Amount Input */}
            <div className="input-group">
              <label>Amount to Convert ({fromCurrency})</label>
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
              {sourceWallet ? (
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Available: {formatCurrency(sourceWallet.balance, sourceWallet.currency)}
                </div>
              ) : (
                <div style={{ fontSize: '0.75rem', color: 'var(--accent-danger)', marginTop: '4px' }}>
                  No {fromCurrency} wallet found. Deposit funds first.
                </div>
              )}
            </div>

            {/* Live Exchange Rate & Conversion Preview */}
            <div
              style={{
                padding: '16px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-glass)',
                border: '1px solid var(--border-focus)',
              }}
            >
              <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <TrendingUp size={14} color="var(--accent-primary)" />
                Live Rate: 1 {fromCurrency} = {rateVal} {toCurrency}
              </div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '6px' }}>
                You Receive: ~{convertedPreview} {toCurrency}
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-lg"
              disabled={isSubmitting || !sourceWallet || parseFloat(sourceWallet.balance) <= 0}
              style={{ marginTop: '8px' }}
            >
              {isSubmitting ? 'Processing Swap...' : `Convert ${fromCurrency} to ${toCurrency}`}
            </button>
          </form>
        </div>

        {/* Conversion Audit History Table */}
        <div className="glass-card" style={{ padding: '28px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '20px' }}>Conversion History</h2>

          {conversions.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
              No conversions recorded yet. Swap currencies above!
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '420px', overflowY: 'auto' }}>
              {conversions.map((c) => (
                <div
                  key={c.id}
                  style={{
                    padding: '14px 16px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-glass)',
                    border: '1px solid var(--border)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <div style={{ fontWeight: 600, fontSize: '0.9375rem' }}>
                      {formatCurrency(c.from_amount, c.from_currency)} → {formatCurrency(c.to_amount, c.to_currency)}
                    </div>
                    <span className="badge badge-credit" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <CheckCircle2 size={12} />
                      Completed
                    </span>
                  </div>

                  <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                    Rate Applied: 1 {c.from_currency} = {c.rate_applied} {c.to_currency}
                  </div>

                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    {formatDate(c.created_at)}
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
