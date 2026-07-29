import React, { useState, useEffect } from 'react';
import { NavBar } from '../components/NavBar';
import { getPortfolioIntelligence } from '../api/portfolio_ai';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { ShieldAlert, ShieldCheck, Zap, Activity, AlertTriangle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const PortfolioAIPage: React.FC = () => {
  const { user } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        if (user) {
          const result = await getPortfolioIntelligence(user.id);
          setData(result);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load portfolio intelligence');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

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

  if (error) {
    return (
      <div className="page-container">
        <NavBar />
        <div className="main-content" style={{ padding: '2rem' }}>
          <div className="error-card">
            <AlertTriangle className="error-icon" />
            <p>{error}</p>
          </div>
        </div>
      </div>
    );
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];
  const pieData = data ? Object.keys(data.sector_allocation).map((key) => ({
    name: key,
    value: data.sector_allocation[key]
  })) : [];

  return (
    <div className="page-container">
      <NavBar />
      <div className="main-content" style={{ padding: '2rem' }}>
        <h1 style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Zap size={32} color="#00C49F" />
          AI Portfolio Intelligence
        </h1>

        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          <div className="card stat-card">
            <div className="stat-icon" style={{ backgroundColor: 'rgba(0, 196, 159, 0.1)', color: '#00C49F' }}>
              <ShieldCheck size={24} />
            </div>
            <div className="stat-content">
              <h3>Diversification Score</h3>
              <div className="stat-value">{data?.diversification_score}/100</div>
            </div>
          </div>
          
          <div className="card stat-card">
            <div className="stat-icon" style={{ backgroundColor: 'rgba(255, 128, 66, 0.1)', color: '#FF8042' }}>
              <ShieldAlert size={24} />
            </div>
            <div className="stat-content">
              <h3>Risk Score</h3>
              <div className="stat-value">{data?.risk_score}/100</div>
            </div>
          </div>

          <div className="card stat-card">
            <div className="stat-icon" style={{ backgroundColor: 'rgba(136, 132, 216, 0.1)', color: '#8884d8' }}>
              <Activity size={24} />
            </div>
            <div className="stat-content">
              <h3>Volatility</h3>
              <div className="stat-value">{data?.volatility}%</div>
            </div>
          </div>
        </div>

        <div className="grid" style={{ gridTemplateColumns: '1fr 2fr', gap: '1.5rem', marginBottom: '2rem' }}>
          <div className="card">
            <h2>Sector Allocation</h2>
            <div style={{ height: '300px', marginTop: '1rem' }}>
              {pieData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
                  No allocation data
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <h2>AI Analysis</h2>
            <div style={{ marginTop: '1.5rem', padding: '1.5rem', backgroundColor: 'var(--surface-hover)', borderRadius: '12px' }}>
              <p style={{ fontSize: '1.1rem', lineHeight: '1.6', marginBottom: '1rem' }}>
                {data?.ai_analysis}
              </p>
              <p style={{ color: 'var(--text-secondary)' }}>
                <strong>Performance Summary:</strong> {data?.performance_summary}
              </p>
            </div>
          </div>
        </div>

        <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
          <div className="card">
            <h2 style={{ color: '#00C49F', marginBottom: '1rem' }}>Advantages</h2>
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {data?.advantages.map((adv: string, i: number) => (
                <li key={i} style={{ marginBottom: '0.8rem', display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
                  <span style={{ color: '#00C49F' }}>✓</span>
                  <span>{adv}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="card">
            <h2 style={{ color: '#FF8042', marginBottom: '1rem' }}>Risks</h2>
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {data?.risks.map((risk: string, i: number) => (
                <li key={i} style={{ marginBottom: '0.8rem', display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
                  <span style={{ color: '#FF8042' }}>!</span>
                  <span>{risk}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="card">
          <h2>Rebalancing Recommendations</h2>
          {data?.recommendations && data.recommendations.length > 0 ? (
            <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {data.recommendations.map((rec: any, i: number) => (
                <div key={i} style={{ padding: '1rem', border: '1px solid var(--border-color)', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <span style={{ 
                      padding: '4px 12px', 
                      borderRadius: '4px', 
                      backgroundColor: rec.action === 'BUY' ? 'rgba(0, 196, 159, 0.1)' : 'rgba(255, 128, 66, 0.1)',
                      color: rec.action === 'BUY' ? '#00C49F' : '#FF8042',
                      fontWeight: 600
                    }}>
                      {rec.action}
                    </span>
                    <strong>{rec.symbol}</strong>
                  </div>
                  <div style={{ color: 'var(--text-secondary)' }}>
                    {rec.reason}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>No rebalancing needed currently.</p>
          )}
        </div>
      </div>
    </div>
  );
};
