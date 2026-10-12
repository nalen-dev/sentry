import { useEffect, useState } from 'react';
import { isWebTarget } from '../data';

/** Ribbon pinned to the top-left corner marking a trial account (web only). */
export default function TrialRibbon() {
  const [plan, setPlan] = useState(() => localStorage.getItem('userPlan'));

  useEffect(() => {
    const sync = () => setPlan(localStorage.getItem('userPlan'));
    window.addEventListener('storage', sync);
    const t = setInterval(sync, 2000);
    return () => {
      window.removeEventListener('storage', sync);
      clearInterval(t);
    };
  }, []);

  if (!isWebTarget || plan !== 'trial') return null;

  return (
    <div
      className="fixed top-0 left-0 w-36 h-36 overflow-hidden pointer-events-none z-[100] select-none"
      title="You are using the Trial version of Sentry SCADA"
    >
      <div 
        className="absolute top-[28px] -left-[45px] w-[180px] -rotate-45 bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 text-black font-black text-[11px] tracking-[0.22em] uppercase py-1.5 text-center shadow-[0_4px_15px_rgba(0,0,0,0.6)] border-y border-amber-300/60"
      >
        TRIAL VERSION
      </div>
    </div>
  );
}
