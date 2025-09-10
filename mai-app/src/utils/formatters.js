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

/**
 * Attempt to fix strings where UTF-8 bytes were decoded as Latin-1 / Windows-1252,
 * resulting in sequences like 'LazÃ£r' instead of 'Lazăr'. Heuristic: re-encode
 * the string as ISO-8859-1 bytes then decode as UTF-8. If the resulting text has
 * fewer replacement chars (�) and contains common diacritics, we return it.
 * Non-destructive: falls back to original if no improvement.
 */
export function decodeMisencodedUTF8(str) {
  if (!str || typeof str !== 'string') return str;
  // Quick check: if already contains Romanian diacritics, keep.
  if (/[ăâîșşţțĂÂÎȘŞŢȚ]/.test(str)) return str;
  try {
    // Encode current (mistaken) Unicode string to bytes as latin1
    const bytes = new Uint8Array(str.length);
    for (let i = 0; i < str.length; i++) bytes[i] = str.charCodeAt(i) & 0xFF;
    const decoded = new TextDecoder('utf-8', { fatal: false }).decode(bytes);
    // If decoded introduces target diacritics and reduces number of replacement chars, use it.
    const replBefore = (str.match(/\uFFFD/g) || []).length;
    const replAfter = (decoded.match(/\uFFFD/g) || []).length;
    const hasDiacritics = /[ăâîșşţțĂÂÎȘŞŢȚ]/.test(decoded);
    if (hasDiacritics && (replAfter < replBefore || replBefore === 0)) return decoded;
    return str;
  } catch {
    return str;
  }
}
