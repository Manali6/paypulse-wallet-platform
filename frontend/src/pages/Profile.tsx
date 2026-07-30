import React, { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../store/authStore';
import { getAssetUrl, handleApiError } from '../lib/api';
import { Camera, Save, Settings, User } from 'lucide-react';
import { Alert } from '../components/ui/Alert';

const CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'INR', 'CAD', 'AUD'];

export const Profile: React.FC = () => {
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const { user, updateProfile, uploadPhoto, isLoading } = useAuthStore();
  const [photoUrl, setPhotoUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [defaultCurrency, setDefaultCurrency] = useState('USD');

  useEffect(() => {
    if (user) {
      setPhotoUrl(user.photo_url || '');
      setDefaultCurrency(user.default_currency || 'USD');
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (selectedFile) {
        await uploadPhoto(selectedFile);
      }
      if (defaultCurrency !== user?.default_currency) {
        await updateProfile({
          default_currency: defaultCurrency,
        });
      }
      setSuccessMsg('Profile updated successfully!');
      setErrorMsg(null);
    } catch (err: any) {
      setErrorMsg(handleApiError(err, 'Failed to update profile'));
      setSuccessMsg(null);
    }
  };

  return (
    <div className="animate-fade-in-up" style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, margin: '0 0 8px 0', color: 'var(--text-primary)' }}>Account Settings</h1>
        <p style={{ color: 'var(--text-secondary)', margin: 0 }}>Manage your profile details and preferences</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        
        {/* Avatar Card */}
        <div className="glass-card" style={{ padding: '32px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px', color: 'var(--text-secondary)' }}>
            <User size={18} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, margin: 0, color: 'var(--text-primary)' }}>Profile Picture</h2>
          </div>
          
          <div 
            style={{ 
              position: 'relative',
              width: '120px', 
              height: '120px', 
              borderRadius: '50%', 
              backgroundColor: 'var(--bg-secondary)', 
              overflow: 'hidden',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid var(--border)',
              cursor: 'pointer',
              boxShadow: 'var(--shadow-lg)',
              transition: 'all var(--transition-fast)'
            }}
            onClick={() => fileInputRef.current?.click()}
            onMouseEnter={(e) => {
              const overlay = e.currentTarget.querySelector('.avatar-overlay') as HTMLElement;
              if (overlay) overlay.style.opacity = '1';
              e.currentTarget.style.borderColor = 'var(--accent-primary)';
              e.currentTarget.style.boxShadow = '0 0 20px rgba(0, 240, 255, 0.3)';
            }}
            onMouseLeave={(e) => {
              const overlay = e.currentTarget.querySelector('.avatar-overlay') as HTMLElement;
              if (overlay) overlay.style.opacity = '0';
              e.currentTarget.style.borderColor = 'var(--border)';
              e.currentTarget.style.boxShadow = 'var(--shadow-lg)';
            }}
          >
            {photoUrl ? (
              <img src={getAssetUrl(photoUrl)} alt="Avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} onError={(e) => (e.currentTarget.style.display = 'none')} />
            ) : (
              <span style={{ fontSize: '3rem', color: 'var(--text-secondary)' }}>
                {user?.display_name?.charAt(0).toUpperCase()}
              </span>
            )}
            
            <div 
              className="avatar-overlay"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(0, 0, 0, 0.6)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                opacity: 0,
                transition: 'opacity var(--transition-fast)'
              }}
            >
              <Camera color="white" size={28} />
            </div>
          </div>
          
          <h3 style={{ margin: '20px 0 4px 0', fontSize: '1.25rem', fontWeight: 600 }}>{user?.display_name}</h3>
          <p style={{ margin: '0', color: 'var(--text-secondary)' }}>{user?.email}</p>
          
          <input
            type="file"
            accept="image/*"
            ref={fileInputRef}
            style={{ display: 'none' }}
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                setSelectedFile(e.target.files[0]);
                setPhotoUrl(URL.createObjectURL(e.target.files[0]));
              }
            }}
          />
        </div>

        {/* Preferences Card */}
        <div className="glass-card" style={{ padding: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px', color: 'var(--text-secondary)' }}>
            <Settings size={18} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, margin: 0, color: 'var(--text-primary)' }}>Preferences</h2>
          </div>
          
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          {errorMsg && <Alert type="error" message={errorMsg} onClose={() => setErrorMsg(null)} />}
          {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}
            <div className="input-group" style={{ marginBottom: '24px', flex: 1 }}>
              <label htmlFor="defaultCurrency">Default Currency</label>
              <select
                id="defaultCurrency"
                className="input"
                value={defaultCurrency}
                onChange={(e) => setDefaultCurrency(e.target.value)}
                style={{ cursor: 'pointer' }}
              >
                {CURRENCIES.map((curr) => (
                  <option key={curr} value={curr} style={{ backgroundColor: 'var(--bg-secondary)' }}>
                    {curr}
                  </option>
                ))}
              </select>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '8px', lineHeight: '1.4' }}>
                Your default currency determines how your total balance is displayed. Changing this will automatically create a wallet in the new currency if you don't already have one.
              </p>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={isLoading}
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', width: '100%', marginTop: 'auto' }}
            >
              <Save size={18} />
              {isLoading ? 'Saving Changes...' : 'Save Changes'}
            </button>
          </form>
        </div>

      </div>
    </div>
  );
};
