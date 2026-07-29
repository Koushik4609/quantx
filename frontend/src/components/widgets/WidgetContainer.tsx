import React from 'react';
import { AlertCircle, Activity } from 'lucide-react';

interface WidgetContainerProps {
  title: string;
  loading?: boolean;
  error?: string | null;
  empty?: boolean;
  emptyMessage?: string;
  children: React.ReactNode;
}

export const WidgetContainer: React.FC<WidgetContainerProps> = ({
  title,
  loading = false,
  error = null,
  empty = false,
  emptyMessage = "No data available.",
  children
}) => {
  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '16px' }}>
      <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-secondary)' }}>{title}</h3>
      
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {loading ? (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100px' }}>
            <Activity size={24} className="animate-spin" color="var(--accent-blue)" />
          </div>
        ) : error ? (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: '8px', color: 'var(--loss)', opacity: 0.8 }}>
            <AlertCircle size={24} />
            <span style={{ fontSize: '13px' }}>{error}</span>
          </div>
        ) : empty ? (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)', fontSize: '13px' }}>
            {emptyMessage}
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
};
