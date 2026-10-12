import { AlertTriangle, X } from 'lucide-react';

interface ConfirmModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
}

export default function ConfirmModal({ 
  isOpen, 
  title, 
  message, 
  onConfirm, 
  onCancel, 
  confirmText = "Confirm", 
  cancelText = "Cancel",
  variant = 'danger'
}: ConfirmModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in">
      <div className="bg-bg-base border border-border rounded-xl shadow-2xl max-w-md w-full overflow-hidden animate-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className={`px-6 py-4 border-b border-border flex items-center justify-between ${variant === 'danger' ? 'bg-red-500/10' : variant === 'warning' ? 'bg-yellow-500/10' : 'bg-scada-primary/10'}`}>
          <div className="flex items-center space-x-3">
            <AlertTriangle className={variant === 'danger' ? 'text-red-500' : variant === 'warning' ? 'text-yellow-500' : 'text-scada-primary'} size={24} />
            <h3 className="font-bold text-lg text-text-primary uppercase tracking-wider">{title}</h3>
          </div>
          <button onClick={onCancel} className="text-text-secondary hover:text-text-primary transition-colors">
            <X size={20} />
          </button>
        </div>
        
        {/* Body */}
        <div className="p-6">
          <p className="text-text-secondary text-sm leading-relaxed whitespace-pre-wrap">{message}</p>
        </div>
        
        {/* Footer */}
        <div className="px-6 py-4 bg-bg-surface border-t border-border flex justify-end space-x-3">
          <button 
            onClick={onCancel}
            className="px-4 py-2 rounded-lg text-sm font-bold text-text-primary bg-bg-panel hover:bg-bg-base border border-border transition-colors"
          >
            {cancelText}
          </button>
          <button 
            onClick={() => { onConfirm(); onCancel(); }}
            className={`px-4 py-2 rounded-lg text-sm font-bold text-bg-base transition-colors ${
              variant === 'danger' ? 'bg-red-500 hover:bg-red-400' : 
              variant === 'warning' ? 'bg-yellow-500 hover:bg-yellow-400' : 
              'bg-scada-primary hover:bg-scada-primary/90'
            }`}
          >
            {confirmText}
          </button>
        </div>
        
      </div>
    </div>
  );
}
