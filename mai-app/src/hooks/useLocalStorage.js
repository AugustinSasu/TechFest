import { useEffect, useState } from 'react';

/**
 * Persist a piece of state in localStorage.
 * Returns [value, setValue, clear].
 */
export function useLocalStorage(key, initialValue) {
  const read = () => {
    try {
      const raw = localStorage.getItem(key);
      return raw !== null ? JSON.parse(raw) : (typeof initialValue === 'function' ? initialValue() : initialValue);
    } catch {
      return typeof initialValue === 'function' ? initialValue() : initialValue;
    }
  };

  const [value, setValue] = useState(read);

  useEffect(() => {
    try {
      if (value === undefined) localStorage.removeItem(key);
      else localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // ignore quota / privacy errors
    }
  }, [key, value]);

  const clear = () => setValue(typeof initialValue === 'function' ? initialValue() : initialValue);

  return [value, setValue, clear];
}
