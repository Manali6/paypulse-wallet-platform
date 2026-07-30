import { describe, it, expect } from 'vitest';
import { formatCurrency, formatDate } from './formatters';

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
});
