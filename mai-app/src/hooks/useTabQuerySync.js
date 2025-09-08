import { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

/**
 * Keeps the ?tab= query in sync with your UI.
 * @param {string[]} validKeys - allowed tab keys
 * @param {string} defaultKey - fallback when missing/invalid
 * @returns {[string, function]} [tab, setTab]
 */
export function useTabQuerySync(validKeys = [], defaultKey = 'overview') {
  const [params, setParams] = useSearchParams();
  const raw = params.get('tab');
  const isValid = raw && (!validKeys.length || validKeys.includes(raw));
  const tab = isValid ? raw : defaultKey;

  // On mount (and when invalid), ensure the URL has a valid tab
  useEffect(() => {
    if (!isValid) {
      const next = new URLSearchParams(params);
      next.set('tab', tab);
      setParams(next, { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isValid, tab]);

  const setTab = (nextKey) => {
    const next = new URLSearchParams(params);
    next.set('tab', nextKey);
    setParams(next, { replace: true });
  };

  return [tab, setTab];
}
