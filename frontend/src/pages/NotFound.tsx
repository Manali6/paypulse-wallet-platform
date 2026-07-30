import React from 'react';
import { Link } from 'react-router-dom';
import { Activity } from 'lucide-react';

export const NotFound: React.FC = () => {
  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
        backgroundColor: 'var(--bg-main)',
      }}
    >
      <div className="glass-card" style={{ width: '100%', maxWidth: '400px', padding: '40px', textAlign: 'center' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '24px' }}>
          <div style={{ 
            width: '64px', 
            height: '64px', 
            borderRadius: '50%', 
            backgroundColor: 'rgba(0, 240, 255, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-primary)',
            boxShadow: '0 0 20px rgba(0, 240, 255, 0.2)'
          }}>
            <Activity size={32} />
          </div>
        </div>
        
        <h1 style={{ fontSize: '3rem', fontWeight: 800, marginBottom: '8px', color: 'var(--text-primary)' }}>404</h1>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '16px', color: 'var(--text-secondary)' }}>Page Not Found</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '32px', lineHeight: '1.5' }}>
          Oops! The page you are looking for doesn't exist or has been moved.
        </p>
        
        <Link to="/" style={{ textDecoration: 'none' }}>
          <button className="btn btn-primary" style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}>
            <Activity size={18} />
            Return to Dashboard
          </button>
        </Link>
      </div>
    </div>
  );
};
