import { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { AlertCircle, CheckCircle, Info, X } from 'lucide-react';

type ToastType = 'success' | 'error' | 'info';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts(prev => [...prev, { id, message, type }]);

    // Auto dismiss after 4 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  }, []);

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {/* Toast Container */}
      <div className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-3 pointer-events-none">
        {toasts.map(toast => (
          <div 
            key={toast.id}
            className={`
              pointer-events-auto flex items-center justify-between min-w-[300px] max-w-[450px] p-4 rounded-xl shadow-2xl backdrop-blur-md border animate-in slide-in-from-right-8 fade-in duration-300
              ${toast.type === 'success' ? 'bg-bg-panel/95 border-scada-success/50' : ''}
              ${toast.type === 'error' ? 'bg-bg-alarm/95 border-red-500/50' : ''}
              ${toast.type === 'info' ? 'bg-bg-panel/95 border-blue-500/50' : ''}
            `}
          >
            <div className="flex items-start">
              <div className="mt-0.5 shrink-0">
                {toast.type === 'success' && <CheckCircle size={20} className="text-scada-success" />}
                {toast.type === 'error' && <AlertCircle size={20} className="text-red-400" />}
                {toast.type === 'info' && <Info size={20} className="text-blue-400" />}
              </div>
              <p className={`ml-3 text-sm font-bold ${toast.type === 'error' ? 'text-white' : 'text-text-primary'}`}>
                {toast.message}
              </p>
            </div>
            <button 
              onClick={() => removeToast(toast.id)}
              className={`ml-4 p-1 rounded-md opacity-60 hover:opacity-100 transition-opacity shrink-0 ${toast.type === 'error' ? 'text-white' : 'text-text-secondary'}`}
            >
              <X size={16} />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}
