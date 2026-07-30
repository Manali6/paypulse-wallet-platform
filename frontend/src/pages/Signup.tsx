import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { handleApiError } from '../lib/api';
import { Alert } from '../components/ui/Alert';
import { Activity } from 'lucide-react';

const CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'INR', 'CAD', 'AUD'];

export const Signup: React.FC = () => {
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [defaultCurrency, setDefaultCurrency] = useState('USD');
  const { signup, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await signup(email, password, displayName, defaultCurrency);
      setSuccessMsg('Account created successfully!');
      setErrorMsg(null);
      navigate('/');
    } catch (err: any) {
      setErrorMsg(handleApiError(err, 'Signup failed'));
      setSuccessMsg(null);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
      }}
    >
      {/* Floating Background */}
      <div className="floating-bg-container">
        <div className="floating-orb cyan"></div>
        <div className="floating-orb purple"></div>
        <div className="floating-orb blue"></div>
      </div>

      <div className="glass-card" style={{ width: '100%', maxWidth: '440px', padding: '32px', position: 'relative', zIndex: 1 }}>
        <div style={{ textAlign: 'center', marginBottom: '32px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: 'var(--radius-sm)', background: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 14px rgba(6, 182, 212, 0.4)' }}>
              <Activity color="white" size={24} />
            </div>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0, color: 'var(--accent-primary)', letterSpacing: '-0.5px' }}>
              PayPulse
            </h2>
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '8px' }}>Create Account</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Set up your multi-currency wallet account
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {errorMsg && <Alert type="error" message={errorMsg} onClose={() => setErrorMsg(null)} />}
          {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}
          <div className="input-group">
            <label htmlFor="displayName">Full Name</label>
            <input
              id="displayName"
              type="text"
              className="input"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="John Doe"
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              minLength={8}
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="defaultCurrency">Default Currency</label>
            <select
              id="defaultCurrency"
              className="input"
              value={defaultCurrency}
              onChange={(e) => setDefaultCurrency(e.target.value)}
            >
              {CURRENCIES.map((curr) => (
                <option key={curr} value={curr} style={{ backgroundColor: 'var(--bg-secondary)' }}>
                  {curr}
                </option>
              ))}
            </select>
          </div>

          <button type="submit" className="btn btn-primary btn-lg" disabled={isLoading} style={{ marginTop: '8px' }}>
            {isLoading ? 'Creating Account...' : 'Get Started'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '24px', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
