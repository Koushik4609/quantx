import React, { useState, useEffect } from 'react';
import { NavBar } from '../components/NavBar';
import { getTransactions } from '../api/trading';
import { AlertCircle, FileText } from 'lucide-react';

export const TransactionsPage: React.FC = () => {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const portfolioId = localStorage.getItem('portfolio_id');

  useEffect(() => {
    const fetchLedger = async () => {
      if (!portfolioId) {
        setError('Portfolio ID missing. Connect in Dashboard first.');
        return;
      }
      setLoading(true);
      try {
        const data = await getTransactions(portfolioId);
        setTransactions(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchLedger();
  }, [portfolioId]);

  return (
    <div>
      <NavBar />
      <div className="page-container animate-fade-in">
        <h1 style={{ fontSize: '28px', marginBottom: '8px' }}>Transaction Ledger</h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>Immutable record of all trading engine events.</p>

        {error ? (
          <div className="error-boundary">
            <AlertCircle size={24} />
            <span style={{ fontWeight: 500 }}>Ledger Sync Failed</span>
            <span style={{ fontSize: '14px' }}>{error}</span>
          </div>
        ) : (
          <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
            {loading ? (
              <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                Fetching ledger records...
              </div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Type</th>
                    <th>Symbol</th>
                    <th>Amount Impact</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.length === 0 ? (
                    <tr>
                      <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '32px' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                          <FileText size={32} opacity={0.5} />
                          <span>No transactions found in the ledger.</span>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    transactions.map((tx: any) => (
                      <tr key={tx.id}>
                        <td style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                          {new Date(tx.created_at).toLocaleString()}
                        </td>
                        <td>
                          <span style={{ 
                            padding: '4px 8px', 
                            borderRadius: '4px', 
                            fontSize: '12px',
                            fontWeight: 600,
                            background: tx.transaction_type === 'BUY' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                            color: tx.transaction_type === 'BUY' ? 'var(--loss)' : 'var(--profit)'
                          }}>
                            {tx.transaction_type}
                          </span>
                        </td>
                        <td style={{ fontWeight: 600 }}>{tx.symbol || 'N/A'}</td>
                        <td style={{ 
                          fontWeight: 500, 
                          color: tx.amount > 0 ? 'var(--profit)' : 'var(--loss)' 
                        }}>
                          {tx.amount > 0 ? '+' : '-'}${Math.abs(tx.amount).toFixed(2)}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
