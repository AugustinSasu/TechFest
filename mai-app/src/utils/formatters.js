/**
 * Common format helpers, pure and dependency-free.
 */

export function formatCurrency(value, currency = 'USD', locale) {
  const n = Number(value) || 0;
  try {
    return new Intl.NumberFormat(locale, { style: 'currency', currency, maximumFractionDigits: 2 }).format(n);
  } catch {
    // Fallback if invalid currency code
    return `${n.toFixed(2)} ${currency}`;
  }
}

export function formatNumber(value, locale, options = {}) {
  const n = Number(value) || 0;
  return new Intl.NumberFormat(locale, options).format(n);
}

export function formatPercent(value, decimals = 0, locale) {
  const n = Number(value) || 0;
  return new Intl.NumberFormat(locale, { style: 'percent', minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(n / 100);
}

export function toK(value, decimals = 1) {
  const n = Number(value) || 0;
  const abs = Math.abs(n);
  const sign = n < 0 ? '-' : '';
  if (abs >= 1e9) return `${sign}${(abs / 1e9).toFixed(decimals)}B`;
  if (abs >= 1e6) return `${sign}${(abs / 1e6).toFixed(decimals)}M`;
  if (abs >= 1e3) return `${sign}${(abs / 1e3).toFixed(decimals)}k`;
  return `${n}`;
}

export function formatDate(iso, locale, opts) {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  const fmt = new Intl.DateTimeFormat(locale, opts || { year: 'numeric', month: 'short', day: '2-digit' });
  return fmt.format(d);
}

export function formatDateTime(iso, locale, opts) {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  const fmt = new Intl.DateTimeFormat(
    locale,
    opts || { year: 'numeric', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' }
  );
  return fmt.format(d);
}

export function clamp(n, min, max) {
  const x = Number(n) || 0;
  return Math.max(min, Math.min(max, x));
}

export function safeNumber(v, fallback = 0) {
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
}
