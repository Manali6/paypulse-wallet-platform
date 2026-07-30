import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Wallet, Send, ArrowRightLeft, LogOut, User as UserIcon } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside
      style={{
        width: 'var(--sidebar-width)',
        height: '100vh',
        position: 'fixed',
        top: 0,
        left: 0,
        backgroundColor: 'var(--bg-secondary)',
        borderRight: '1px solid var(--bg-glass-border)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '24px 16px',
        zIndex: 100,
      }}
    >
      <div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '0 12px 24px 12px',
            borderBottom: '1px solid var(--border)',
            marginBottom: '24px',
          }}
        >
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--accent-gradient)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 800,
              color: '#fff',
            }}
          >
            W
          </div>
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700, lineHeight: 1.2 }}>
              PayPulse
            </h2>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Wallet Platform
            </span>
          </div>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <NavLink
            to="/"
            end
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
              backgroundColor: isActive ? 'var(--bg-glass)' : 'transparent',
              border: isActive ? '1px solid var(--border-focus)' : '1px solid transparent',
              fontWeight: isActive ? 600 : 500,
            })}
          >
            <LayoutDashboard size={18} />
            Dashboard
          </NavLink>

          <NavLink
            to="/wallets"
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
              backgroundColor: isActive ? 'var(--bg-glass)' : 'transparent',
              border: isActive ? '1px solid var(--border-focus)' : '1px solid transparent',
              fontWeight: isActive ? 600 : 500,
            })}
          >
            <Wallet size={18} />
            Wallets
          </NavLink>

          <NavLink
            to="/transfers"
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
              backgroundColor: isActive ? 'var(--bg-glass)' : 'transparent',
              border: isActive ? '1px solid var(--border-focus)' : '1px solid transparent',
              fontWeight: isActive ? 600 : 500,
            })}
          >
            <Send size={18} />
            Transfers
          </NavLink>

          <NavLink
            to="/exchange"
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
              backgroundColor: isActive ? 'var(--bg-glass)' : 'transparent',
              border: isActive ? '1px solid var(--border-focus)' : '1px solid transparent',
              fontWeight: isActive ? 600 : 500,
            })}
          >
            <ArrowRightLeft size={18} />
            Exchange
          </NavLink>

          <NavLink
            to="/profile"
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
              backgroundColor: isActive ? 'var(--bg-glass)' : 'transparent',
              border: isActive ? '1px solid var(--border-focus)' : '1px solid transparent',
              fontWeight: isActive ? 600 : 500,
            })}
          >
            <UserIcon size={18} />
            Profile
          </NavLink>
        </nav>
      </div>

      <div style={{ borderTop: '1px solid var(--border)', paddingTop: '16px' }}>
        {user && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '8px 12px',
              marginBottom: '12px',
            }}
          >
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                backgroundColor: 'var(--bg-glass)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--accent-primary)',
                overflow: 'hidden',
                border: '1px solid var(--border)',
              }}
            >
              {user.photo_url ? (
                <img src={user.photo_url} alt="Avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} onError={(e) => (e.currentTarget.style.display = 'none')} />
              ) : (
                <UserIcon size={18} />
              )}
            </div>
            <div style={{ overflow: 'hidden' }}>
              <div
                style={{
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {user.display_name}
              </div>
              <div
                style={{
                  fontSize: '0.75rem',
                  color: 'var(--text-muted)',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {user.email}
              </div>
            </div>
          </div>
        )}

        <button
          onClick={handleLogout}
          className="btn btn-secondary"
          style={{ width: '100%', justifyContent: 'flex-start' }}
        >
          <LogOut size={16} />
          Log Out
        </button>
      </div>
    </aside>
  );
};
