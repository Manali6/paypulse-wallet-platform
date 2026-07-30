import React from 'react';

interface AlertProps {
  type: 'error' | 'success';
  message: string;
  onClose?: () => void;
}

export const Alert: React.FC<AlertProps> = ({ type, message, onClose }) => {
  if (!message) return null;

  const isError = type === 'error';
  const bgColor = isError ? 'rgba(255, 59, 48, 0.1)' : 'rgba(52, 199, 89, 0.1)';
  const textColor = isError ? '#ff3b30' : '#34c759';
  const borderColor = isError ? 'rgba(255, 59, 48, 0.2)' : 'rgba(52, 199, 89, 0.2)';

  return (
    <div style={{
      backgroundColor: bgColor,
      color: textColor,
      padding: '12px 16px',
      borderRadius: '8px',
      marginBottom: '20px',
      border: `1px solid ${borderColor}`,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      fontSize: '0.9rem',
      fontWeight: 500,
      animation: 'fadeIn 0.3s ease-in-out'
    }}>
      <span>{message}</span>
      {onClose && (
        <button 
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: textColor,
            cursor: 'pointer',
            padding: '4px',
            opacity: 0.7,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
          onMouseLeave={(e) => e.currentTarget.style.opacity = '0.7'}
        >
          ×
        </button>
      )}
    </div>
  );
};
