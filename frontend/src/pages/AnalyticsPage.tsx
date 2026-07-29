import React, { useState, useEffect } from 'react';
import { NavBar } from '../components/NavBar';
import { getScreener, getHeatmap, getFinancials, getCalendar, getInstitutional, getInsider } from '../api/analytics';
import type { ScreenerStock, HeatmapSector, FinancialStatement, CalendarEvent, InstitutionalHolder, InsiderTrade } from '../api/analytics';
import { Activity, LayoutGrid, Calendar, Users, Briefcase, TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('screener');
  const [loading, setLoading] = useState(true);
  
  const [screener, setScreener] = useState<ScreenerStock[]>([]);
  const [heatmap, setHeatmap] = useState<HeatmapSector[]>([]);
  const [calendar, setCalendar] = useState<CalendarEvent[]>([]);
  
  const [selectedTicker, setSelectedTicker] = useState('AAPL');
  const [financials, setFinancials] = useState<FinancialStatement[]>([]);
  const [institutional, setInstitutional] = useState<InstitutionalHolder[]>([]);
  const [insider, setInsider] = useState<InsiderTrade[]>([]);
  const [tickerLoading, setTickerLoading] = useState(false);

  useEffect(() => {
    loadGlobalData();
  }, []);

  useEffect(() => {
    if (['financials', 'institutional', 'insider'].includes(activeTab)) {
      loadTickerData(selectedTicker);
    }
  }, [activeTab, selectedTicker]);

  const loadGlobalData = async () => {
    setLoading(true);
    try {
      const [s, h, c] = await Promise.all([
        getScreener(),
        getHeatmap(),
        getCalendar()
      ]);
      setScreener(s);
      setHeatmap(h);
      setCalendar(c);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const loadTickerData = async (ticker: string) => {
    setTickerLoading(true);
    try {
      const [f, i, t] = await Promise.all([
        getFinancials(ticker),
        getInstitutional(ticker),
        getInsider(ticker)
      ]);
      setFinancials(f);
      setInstitutional(i);
      setInsider(t);
    } catch (e) {
      console.error(e);
    } finally {
      setTickerLoading(false);
    }
  };

  const tabs = [
    { id: 'screener', label: 'Stock Screener', icon: LayoutGrid },
    { id: 'heatmap', label: 'Market Heatmap', icon: Activity },
    { id: 'calendar', label: 'Earnings Calendar', icon: Calendar },
    { id: 'financials', label: 'Financial Statements', icon: Briefcase },
    { id: 'institutional', label: 'Institutional Holdings', icon: Users },
    { id: 'insider', label: 'Insider Trades', icon: Users }
  ];

  const formatNumber = (num?: number) => {
    if (num === undefined || num === null) return '-';
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    return `$${num.toLocaleString()}`;
  };

  const renderScreener = () => (
    <div className="glass-panel" style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Symbol</th>
            <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Price</th>
            <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Change %</th>
            <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Volume</th>
            <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Market Cap</th>
            <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Sector</th>
          </tr>
        </thead>
        <tbody>
          {screener.map(stock => (
            <tr key={stock.symbol} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              <td style={{ padding: '16px', fontWeight: 600 }}>{stock.symbol}</td>
              <td style={{ padding: '16px' }}>${stock.price.toFixed(2)}</td>
              <td style={{ padding: '16px', color: stock.change_percent >= 0 ? 'var(--profit)' : 'var(--loss)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                {stock.change_percent >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                {Math.abs(stock.change_percent).toFixed(2)}%
              </td>
              <td style={{ padding: '16px' }}>{stock.volume.toLocaleString()}</td>
              <td style={{ padding: '16px' }}>{formatNumber(stock.market_cap)}</td>
              <td style={{ padding: '16px' }}>{stock.sector}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderHeatmap = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {heatmap.map(sector => (
        <div key={sector.sector}>
          <h3 style={{ fontSize: '18px', marginBottom: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span>{sector.sector}</span>
            <span style={{ color: sector.performance >= 0 ? 'var(--profit)' : 'var(--loss)', fontSize: '14px' }}>
              {sector.performance > 0 ? '+' : ''}{sector.performance.toFixed(2)}%
            </span>
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: '8px' }}>
            {sector.stocks.map(stock => {
              const intensity = Math.min(Math.abs(stock.change_percent) / 3, 1); // Normalize up to 3%
              const bgColor = stock.change_percent >= 0 
                ? `rgba(16, 185, 129, ${0.2 + intensity * 0.8})` // Green
                : `rgba(239, 68, 68, ${0.2 + intensity * 0.8})`; // Red

              return (
                <div key={stock.symbol} style={{ background: bgColor, padding: '16px', borderRadius: '8px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
                  <span style={{ fontWeight: 600, fontSize: '16px' }}>{stock.symbol}</span>
                  <span style={{ fontSize: '12px', opacity: 0.9 }}>{stock.change_percent > 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%</span>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );

  const renderTickerSelector = () => (
    <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', alignItems: 'center' }}>
      <label style={{ color: 'var(--text-secondary)' }}>Select Ticker:</label>
      <select 
        value={selectedTicker} 
        onChange={(e) => setSelectedTicker(e.target.value)}
        className="input-field"
        style={{ width: '200px' }}
      >
        {screener.map(s => <option key={s.symbol} value={s.symbol}>{s.symbol}</option>)}
      </select>
      {tickerLoading && <Activity className="animate-spin" size={16} color="var(--text-secondary)" />}
    </div>
  );

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <NavBar />
      
      <div className="page-container animate-fade-in" style={{ flex: 1, paddingBottom: '48px' }}>
        <div style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '28px', marginBottom: '8px' }}>Market Analytics</h1>
            <p style={{ color: 'var(--text-secondary)' }}>Professional live market data and institutional insights.</p>
          </div>
          <button onClick={loadGlobalData} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <RefreshCw size={16} /> Refresh Data
          </button>
        </div>

        <div style={{ display: 'flex', gap: '12px', marginBottom: '32px', overflowX: 'auto', paddingBottom: '8px' }}>
          {tabs.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 20px', borderRadius: '8px',
                  background: isActive ? 'var(--accent-blue)' : 'rgba(255,255,255,0.05)',
                  color: isActive ? '#fff' : 'var(--text-secondary)',
                  border: 'none', cursor: 'pointer', whiteSpace: 'nowrap', transition: 'all 0.2s', fontWeight: 500
                }}
              >
                <Icon size={18} />
                {tab.label}
              </button>
            )
          })}
        </div>

        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '64px' }}>
            <Activity className="animate-spin" size={32} color="var(--accent-blue)" />
          </div>
        ) : (
          <div>
            {activeTab === 'screener' && renderScreener()}
            {activeTab === 'heatmap' && renderHeatmap()}
            
            {['financials', 'institutional', 'insider'].includes(activeTab) && renderTickerSelector()}
            
            {activeTab === 'financials' && !tickerLoading && (
              <div className="glass-panel" style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Date</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Total Revenue</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Net Income</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Operating Income</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Total Assets</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Total Liabilities</th>
                    </tr>
                  </thead>
                  <tbody>
                    {financials.map(f => (
                      <tr key={f.date} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <td style={{ padding: '16px', fontWeight: 600 }}>{f.date}</td>
                        <td style={{ padding: '16px' }}>{formatNumber(f.total_revenue)}</td>
                        <td style={{ padding: '16px', color: (f.net_income || 0) >= 0 ? 'var(--profit)' : 'var(--loss)' }}>{formatNumber(f.net_income)}</td>
                        <td style={{ padding: '16px' }}>{formatNumber(f.operating_income)}</td>
                        <td style={{ padding: '16px' }}>{formatNumber(f.total_assets)}</td>
                        <td style={{ padding: '16px' }}>{formatNumber(f.total_liabilities)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            
            {activeTab === 'institutional' && !tickerLoading && (
              <div className="glass-panel" style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Institution</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Shares Held</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>% Outstanding</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Date Reported</th>
                    </tr>
                  </thead>
                  <tbody>
                    {institutional.map((h, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <td style={{ padding: '16px', fontWeight: 600 }}>{h.holder}</td>
                        <td style={{ padding: '16px' }}>{h.shares.toLocaleString()}</td>
                        <td style={{ padding: '16px' }}>{(h.percent_out * 100).toFixed(2)}%</td>
                        <td style={{ padding: '16px' }}>{h.date_reported}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            
            {activeTab === 'insider' && !tickerLoading && (
              <div className="glass-panel" style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Insider Name</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Position</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Transaction</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Shares</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Value</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {insider.map((trade, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <td style={{ padding: '16px', fontWeight: 600 }}>{trade.insider}</td>
                        <td style={{ padding: '16px', color: 'var(--text-secondary)', fontSize: '14px' }}>{trade.position}</td>
                        <td style={{ padding: '16px', color: trade.transaction_type === 'Buy' ? 'var(--profit)' : 'var(--loss)' }}>{trade.transaction_type}</td>
                        <td style={{ padding: '16px' }}>{trade.shares.toLocaleString()}</td>
                        <td style={{ padding: '16px' }}>{formatNumber(trade.value)}</td>
                        <td style={{ padding: '16px' }}>{trade.date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            
            {activeTab === 'calendar' && (
              <div className="glass-panel" style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Symbol</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Date</th>
                      <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Event Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {calendar.length === 0 && (
                      <tr>
                        <td colSpan={3} style={{ padding: '32px', textAlign: 'center', color: 'var(--text-secondary)' }}>No upcoming calendar events found.</td>
                      </tr>
                    )}
                    {calendar.map((ev, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <td style={{ padding: '16px', fontWeight: 600 }}>{ev.symbol}</td>
                        <td style={{ padding: '16px' }}>{ev.date}</td>
                        <td style={{ padding: '16px', textTransform: 'capitalize' }}>{ev.type}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            
          </div>
        )}
      </div>
    </div>
  );
};
