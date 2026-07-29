import React, { useState, useEffect } from 'react';
import { NavBar } from '../components/NavBar';
import { getBrokerStatus, getBrokerLoginUrl, getBrokerProfile, getBrokerFunds, getBrokerHoldings, getBrokerOrders } from '../api/broker';
import { Shield, Link as LinkIcon, AlertTriangle, TrendingUp, DollarSign, Briefcase, Activity } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const BrokerPage: React.FC = () => {
  const { user } = useAuth();
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [profile, setProfile] = useState<any>(null);
  const [funds, setFunds] = useState<any>(null);
  const [holdings, setHoldings] = useState<any>(null);
  const [orders, setOrders] = useState<any>(null);

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      setLoading(true);
      const res = await getBrokerStatus();
      setConnected(res.connected);
      if (res.connected) {
        await loadBrokerData();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to check broker status');
    } finally {
      setLoading(false);
    }
  };

  const loadBrokerData = async () => {
    try {
      const [prof, fnd, hold, ord] = await Promise.all([
        getBrokerProfile(),
        getBrokerFunds(),
        getBrokerHoldings(),
        getBrokerOrders()
      ]);
      setProfile(prof.data);
      setFunds(fnd.data);
      setHoldings(hold.data);
      setOrders(ord.data);
    } catch (err: any) {
      setError('Failed to fetch data from broker. Access token might be expired.');
    }
  };

  const handleConnect = async () => {
    try {
      const url = await getBrokerLoginUrl();
      window.location.href = url;
    } catch (err: any) {
      setError(err.message || 'Failed to get login URL');
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <NavBar />
        <div className="main-content" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <NavBar />
      <div className="main-content" style={{ padding: '2rem' }}>
        <h1 style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Shield size={32} color="#8884d8" />
          Broker Integration
        </h1>

        {error && (
          <div className="error-card" style={{ marginBottom: '2rem' }}>
            <AlertTriangle className="error-icon" />
            <p>{error}</p>
          </div>
        )}

        {!connected ? (
          <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
            <LinkIcon size={64} style={{ opacity: 0.2, marginBottom: '2rem' }} />
            <h2>Connect Your Broker</h2>
            <p style={{ color: 'var(--text-secondary)', marginTop: '1rem', marginBottom: '2rem', maxWidth: '500px', margin: '1rem auto 2rem' }}>
              Securely connect your Upstox account to unlock live trading, sync your real portfolio, and execute AI-generated strategies directly.
            </p>
            <button onClick={handleConnect} className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
              <LinkIcon size={20} />
              Connect Upstox
            </button>
          </div>
        ) : (
          <div>
            <div className="card" style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderLeft: '4px solid #00C49F' }}>
              <div>
                <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#00C49F' }}>
                  <Shield size={24} /> Upstox Connected
                </h2>
                <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                  Logged in as {profile?.user_name || user?.email}
                </p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Available Margin</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>₹{funds?.equity?.available_margin?.toFixed(2) || '0.00'}</div>
              </div>
            </div>

            <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem' }}>
              <div className="card">
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                  <Briefcase size={20} /> Live Holdings
                </h3>
                {holdings && holdings.length > 0 ? (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Symbol</th>
                        <th>Qty</th>
                        <th>Avg Price</th>
                        <th>LTP</th>
                        <th>P&L</th>
                      </tr>
                    </thead>
                    <tbody>
                      {holdings.map((h: any, i: number) => {
                        const pnl = (h.last_price - h.average_price) * h.quantity;
                        const isProfit = pnl >= 0;
                        return (
                          <tr key={i}>
                            <td><strong>{h.tradingsymbol}</strong></td>
                            <td>{h.quantity}</td>
                            <td>₹{h.average_price}</td>
                            <td>₹{h.last_price}</td>
                            <td style={{ color: isProfit ? '#00C49F' : '#FF8042' }}>
                              {isProfit ? '+' : ''}₹{pnl.toFixed(2)}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                ) : (
                  <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '2rem' }}>No holdings found.</p>
                )}
              </div>

              <div className="card">
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                  <Activity size={20} /> Recent Orders
                </h3>
                {orders && orders.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {orders.slice(0, 5).map((o: any, i: number) => (
                      <div key={i} style={{ padding: '1rem', backgroundColor: 'var(--surface-hover)', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ fontWeight: 600 }}>{o.tradingsymbol}</div>
                          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                            {o.transaction_type} • {o.quantity} qty
                          </div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <span style={{ 
                            padding: '4px 8px', 
                            borderRadius: '4px',
                            fontSize: '0.85rem',
                            backgroundColor: o.status === 'complete' ? 'rgba(0,196,159,0.1)' : 'rgba(255,187,40,0.1)',
                            color: o.status === 'complete' ? '#00C49F' : '#FFBB28'
                          }}>
                            {o.status.toUpperCase()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '2rem' }}>No orders found.</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
