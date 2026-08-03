'use client';

import { useEffect, useState } from 'react';

/**
 * Layout is handled entirely in CSS at the 820px breakpoint. This hook exists
 * only for the handful of things CSS cannot express — currently the composer's
 * placeholder text. It starts false so server and client agree on first paint.
 */
export function useIsDesktop() {
  const [isDesktop, setIsDesktop] = useState(false);

  useEffect(() => {
    const query = window.matchMedia('(min-width: 820px)');
    const sync = () => setIsDesktop(query.matches);
    sync();
    query.addEventListener('change', sync);
    return () => query.removeEventListener('change', sync);
  }, []);

  return isDesktop;
}
