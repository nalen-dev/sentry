import { useEffect, useState } from 'react';
import { isWebTarget } from '../data';

const MOBILE_QUERY = '(max-width: 767px)';

/**
 * True on phone-sized viewports. Only the web build has a mobile layout;
 * the desktop (Tauri) app always uses the desktop layout.
 */
export function useIsMobile(): boolean {
  const get = () => isWebTarget && typeof window !== 'undefined' && window.matchMedia(MOBILE_QUERY).matches;
  const [isMobile, setIsMobile] = useState(get);

  useEffect(() => {
    if (!isWebTarget) return;
    const mq = window.matchMedia(MOBILE_QUERY);
    const onChange = () => setIsMobile(mq.matches);
    onChange();
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, []);

  return isMobile;
}
