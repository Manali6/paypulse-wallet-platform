import { describe, it, expect } from 'vitest';
import { formatCurrency, formatDate, formatRelativeTime } from './formatters';

describe('formatters', () => {
  describe('formatCurrency', () => {
    it('formats USD correctly', () => {
      expect(formatCurrency('1234.56', 'USD')).toBe('$1,234.56');
    });

    it('formats EUR correctly', () => {
      // Intl format output varies slightly by node environment, 
      // but it should contain the Euro symbol
      const result = formatCurrency('1234.56', 'EUR');
      expect(result).toContain('1,234.56');
      expect(result).toContain('€');
    });

    it('handles zero balances gracefully', () => {
      expect(formatCurrency('0', 'GBP')).toContain('£0.00');
    });
  });

  describe('formatDate', () => {
    it('formats ISO date strings correctly', () => {
      const dateString = '2023-12-25T15:30:00Z';
      const result = formatDate(dateString);
      expect(result).toContain('Dec 25, 2023');
    });
  });

  describe('formatRelativeTime', () => {
    it('returns "just now" for dates within a minute', () => {
      const now = new Date();
      expect(formatRelativeTime(now.toISOString())).toBe('just now');
    });

    it('returns "m ago" for dates within an hour', () => {
      const past = new Date(Date.now() - 5 * 60 * 1000); // 5 minutes ago
      expect(formatRelativeTime(past.toISOString())).toBe('5m ago');
    });

    it('returns "h ago" for dates within a day', () => {
      const past = new Date(Date.now() - 3 * 60 * 60 * 1000); // 3 hours ago
      expect(formatRelativeTime(past.toISOString())).toBe('3h ago');
    });

    it('returns "d ago" for dates within a week', () => {
      const past = new Date(Date.now() - 2 * 24 * 60 * 60 * 1000); // 2 days ago
      expect(formatRelativeTime(past.toISOString())).toBe('2d ago');
    });

    it('falls back to formatDate for older dates', () => {
      const past = new Date(Date.now() - 10 * 24 * 60 * 60 * 1000); // 10 days ago
      expect(formatRelativeTime(past.toISOString())).toContain(new Date().getFullYear().toString());
    });
  });
});
