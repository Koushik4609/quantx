import React, { useState, useEffect } from 'react';
import { NavBar } from '../components/NavBar';
import { getAlerts, createAlert, deleteAlert, type Alert } from '../api/alerts';
import { Bell, BellRing, Plus, Trash2, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';

export const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [symbol, setSymbol] = useState('AAPL');
  const [alertType, setAlertType] = useState('PRICE');
  const [condition, setCondition] = useState('ABOVE');
  const [value, setValue] = useState(150);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const data = await getAlerts();
      setAlerts(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch alerts');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createAlert({ symbol, alert_type: alertType, condition, value });
      fetchAlerts();
    } catch (err: any) {
      setError(err.message || 'Failed to create alert');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteAlert(id);
      fetchAlerts();
    } catch (err: any) {
      setError(err.message || 'Failed to delete alert');
    }
  };

  return (
    <div className="page-container">
      <NavBar />
      <div className="main-content" style={{ padding: '2rem' }}>
        <h1 style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Bell size={32} color="var(--primary-color)" />
          Market Alerts
        </h1>

        {error && (
          <div className="error-card" style={{ marginBottom: '2rem' }}>
            <AlertTriangle className="error-icon" />
            <p>{error}</p>
          </div>
        )}

        <div className="grid" style={{ gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
          <div className="card">
            <h2>Create Alert</h2>
            <form onSubmit={handleCreate} style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label>Symbol</label>
                <input 
                  type="text" 
                  value={symbol} 
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  required
                />
              </div>

              <div className="form-group">
                <label>Type</label>
                <select value={alertType} onChange={(e) => setAlertType(e.target.value)}>
                  <option value="PRICE">Price</option>
                  <option value="VOLUME">Volume</option>
                  <option value="RSI">RSI</option>
                  <option value="MACD">MACD</option>
                </select>
              </div>

              <div className="form-group">
                <label>Condition</label>
                <select value={condition} onChange={(e) => setCondition(e.target.value)}>
                  <option value="ABOVE">Goes Above</option>
                  <option value="BELOW">Goes Below</option>
                  <option value="EQUAL">Is Exactly</option>
                </select>
              </div>

              <div className="form-group">
                <label>Value</label>
                <input 
                  type="number" 
                  step="0.01"
                  value={value} 
                  onChange={(e) => setValue(parseFloat(e.target.value))}
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem', display: 'flex', justifyContent: 'center', gap: '0.5rem' }}>
                <Plus size={20} /> Create Alert
              </button>
            </form>
          </div>

          <div className="card">
            <h2>Active & Triggered Alerts</h2>
            {loading ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
                <div className="loading-spinner"></div>
              </div>
            ) : alerts.length === 0 ? (
              <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '3rem' }}>
                <Bell size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
                <p>No alerts configured yet.</p>
              </div>
            ) : (
              <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {alerts.map((alert) => (
                  <div key={alert.id} style={{ 
                    padding: '1.25rem', 
                    borderRadius: '12px', 
                    backgroundColor: 'var(--surface-hover)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    borderLeft: `4px solid ${alert.status === 'TRIGGERED' ? '#FFBB28' : '#00C49F'}`
                  }}>
                    <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
                      <div style={{ 
                        width: '40px', height: '40px', borderRadius: '50%', 
                        backgroundColor: alert.status === 'TRIGGERED' ? 'rgba(255,187,40,0.1)' : 'rgba(0,196,159,0.1)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: alert.status === 'TRIGGERED' ? '#FFBB28' : '#00C49F'
                      }}>
                        {alert.status === 'TRIGGERED' ? <BellRing size={20} /> : <Bell size={20} />}
                      </div>
                      
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                          <strong style={{ fontSize: '1.1rem' }}>{alert.symbol}</strong>
                          <span style={{ 
                            fontSize: '0.75rem', 
                            padding: '2px 8px', 
                            borderRadius: '12px', 
                            backgroundColor: 'rgba(255,255,255,0.05)' 
                          }}>
                            {alert.alert_type}
                          </span>
                        </div>
                        <div style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          {alert.condition === 'ABOVE' ? <TrendingUp size={16} color="#00C49F" /> : <TrendingDown size={16} color="#FF8042" />}
                          {alert.condition.toLowerCase()} {alert.value}
                        </div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontWeight: 600, color: alert.status === 'TRIGGERED' ? '#FFBB28' : '#00C49F' }}>
                          {alert.status}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                          {new Date(alert.created_at || '').toLocaleDateString()}
                        </div>
                      </div>
                      <button 
                        onClick={() => alert.id && handleDelete(alert.id)}
                        style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '0.5rem' }}
                        title="Delete Alert"
                      >
                        <Trash2 size={20} className="hover-red" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
