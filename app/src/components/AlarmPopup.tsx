import { useEffect, useRef } from 'react';
import { AlertTriangle, CheckCircle } from 'lucide-react';
import { SegmentData } from './SegmentDetailModal';

interface AlarmPopupProps {
  unackedAlarms: SegmentData[];
  onAck: (ids: number[]) => void;
  onCancel: () => void;
}

export default function AlarmPopup({ unackedAlarms, onAck, onCancel }: AlarmPopupProps) {
  const audioCtxRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    if (unackedAlarms.length > 0) {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioContextClass) return;
      
      const ctx = new AudioContextClass();
      audioCtxRef.current = ctx;
      
      const oscillator = ctx.createOscillator();
      const gainNode = ctx.createGain();
      
      oscillator.type = 'square';
      oscillator.frequency.setValueAtTime(800, ctx.currentTime);
      
      gainNode.gain.value = 0;
      
      let isBeeping = false;
      const interval = setInterval(() => {
        isBeeping = !isBeeping;
        gainNode.gain.setTargetAtTime(isBeeping ? 0.3 : 0, ctx.currentTime, 0.05);
      }, 500);

      oscillator.connect(gainNode);
      gainNode.connect(ctx.destination);
      oscillator.start();
      
      return () => {
        clearInterval(interval);
        try { oscillator.stop(); } catch(e) {}
        ctx.close();
      };
    }
  }, [unackedAlarms]);

  if (unackedAlarms.length === 0) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-bg-panel border-2 border-red-500 rounded-xl shadow-[0_0_40px_rgba(239,68,68,0.3)] max-w-md w-full p-6 animate-[pulse_2s_infinite]">
        <div className="flex items-center space-x-3 text-red-500 mb-4">
          <AlertTriangle size={32} />
          <h2 className="text-xl font-bold uppercase tracking-widest">CRITICAL ALARM</h2>
        </div>
        
        <div className="max-h-48 overflow-y-auto mb-6 space-y-2 custom-scrollbar pr-2">
          {unackedAlarms.map(a => (
            <div key={a.id} className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
              <div className="flex justify-between font-bold">
                <span className="text-text-primary">{a.name}</span>
                <span className="text-red-400">{a.temp_max}°C</span>
              </div>
              <div className="text-xs text-text-secondary mt-1">{a.status}</div>
            </div>
          ))}
        </div>
        
        <div className="flex space-x-3">
          <button 
            onClick={() => onAck(unackedAlarms.map(a => a.id))}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-lg flex items-center justify-center transition-colors"
          >
            <CheckCircle size={18} className="mr-2" />
            ACKNOWLEDGE
          </button>
          <button 
            onClick={onCancel}
            className="px-6 bg-bg-surface hover:bg-bg-base border border-border text-text-secondary hover:text-text-primary font-bold py-3 rounded-lg flex items-center justify-center transition-colors"
          >
            CANCEL
          </button>
        </div>
      </div>
    </div>
  );
}
