import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { getAssetUrl } from '../lib/api';
import toast from 'react-hot-toast';

const CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'INR', 'CAD', 'AUD'];

export const Profile: React.FC = () => {
  const { user, updateProfile, uploadPhoto, isLoading } = useAuthStore();
  const [photoUrl, setPhotoUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
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
      toast.success('Profile updated successfully!');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to update profile');
    }
  };

  return (
    <div className="container" style={{ maxWidth: '600px', marginTop: '40px' }}>
      <div className="card">
        <h2 style={{ marginBottom: '24px' }}>Profile Settings</h2>
        
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px', gap: '16px' }}>
            <div style={{ 
              width: '80px', 
              height: '80px', 
              borderRadius: '50%', 
              backgroundColor: 'var(--bg-secondary)', 
              overflow: 'hidden',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid var(--border-color)'
            }}>
              {photoUrl ? (
                <img src={getAssetUrl(photoUrl)} alt="Avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} onError={(e) => (e.currentTarget.style.display = 'none')} />
              ) : (
                <span style={{ fontSize: '2rem', color: 'var(--text-secondary)' }}>
                  {user?.display_name?.charAt(0).toUpperCase()}
                </span>
              )}
            </div>
            <div style={{ flex: 1 }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem' }}>{user?.display_name}</h3>
              <p style={{ margin: '4px 0 0', color: 'var(--text-secondary)' }}>{user?.email}</p>
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="photoUpload">Profile Picture</label>
            <input
              id="photoUpload"
              type="file"
              accept="image/*"
              className="input"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setSelectedFile(e.target.files[0]);
                  setPhotoUrl(URL.createObjectURL(e.target.files[0]));
                }
              }}
              style={{ paddingTop: '8px' }}
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
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Changing this will automatically create a wallet in the new currency if you don't have one.
            </p>
          </div>

          <button type="submit" className="btn btn-primary" disabled={isLoading}>
            {isLoading ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>
    </div>
  );
};
