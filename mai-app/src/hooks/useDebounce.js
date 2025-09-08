import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

/**
 * Returns a debounced value that updates only after `delay` ms.
 */
export function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

/**
 * Returns a debounced callback.
 */
export function useDebouncedCallback(fn, delay = 300, deps = []) {
  const fnRef = useRef(fn);
  useEffect(() => {
    fnRef.current = fn;
  }, [fn]);

  return useMemo(() => {
    let t;
    const wrapped = (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fnRef.current?.(...args), delay);
    };
    wrapped.cancel = () => clearTimeout(t);
    return wrapped;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [delay, ...deps]);
}
