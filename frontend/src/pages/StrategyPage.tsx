import React, { useState, useEffect } from 'react';
import { NavBar } from '../components/NavBar';
import { getStrategies, createStrategy, deleteStrategy, runBacktest, getBacktests } from '../api/strategy';
import type { Strategy, StrategyCondition, BacktestResult } from '../api/strategy';
import { Activity, Play, Plus, Trash2, Settings, Zap } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export const StrategyPage: React.FC = () => {
  const userId = localStorage.getItem('user_id') || '00000000-0000-0000-0000-000000000000';
  
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [activeStrategy, setActiveStrategy] = useState<Strategy | null>(null);
  const [backtests, setBacktests] = useState<BacktestResult[]>([]);
  const [runningTest, setRunningTest] = useState(false);
  const [activeResult, setActiveResult] = useState<BacktestResult | null>(null);

  // Builder State
  const [showBuilder, setShowBuilder] = useState(false);
  const [bName, setBName] = useState('New Strategy');
  const [bSymbol, setBSymbol] = useState('AAPL');
  const [bTimeframe, setBTimeframe] = useState('1d');
  const [entryConds, setEntryConds] = useState<StrategyCondition[]>([{ indicator: 'RSI', operator: '<', value: 30, timeperiod: 14 }]);
  const [exitConds, setExitConds] = useState<StrategyCondition[]>([{ indicator: 'RSI', operator: '>', value: 70, timeperiod: 14 }]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    setLoading(true);
    try {
      const res = await getStrategies(userId);
      setStrategies(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectStrategy = async (strat: Strategy) => {
    setActiveStrategy(strat);
    setShowBuilder(false);
    setActiveResult(null);
    try {
      const bts = await getBacktests(strat.id);
      setBacktests(bts);
      if (bts.length > 0) setActiveResult(bts[0]);
    } catch (e) {
      console.error(e);
    }
  };

  const handleRunBacktest = async () => {
    if (!activeStrategy) return;
    setRunningTest(true);
    try {
      const res = await runBacktest(activeStrategy.id);
      setBacktests([res, ...backtests]);
      setActiveResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setRunningTest(false);
    }
  };

  const handleSaveStrategy = async () => {
    setSaving(true);
    try {
      const newStrat = await createStrategy(userId, {
        name: bName,
        symbol: bSymbol,
        timeframe: bTimeframe,
        conditions: { entry: entryConds, exit: exitConds }
      });
      setStrategies([...strategies, newStrat]);
      setShowBuilder(false);
      handleSelectStrategy(newStrat);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteStrategy = async (id: string) => {
    try {
      await deleteStrategy(id);
      setStrategies(strategies.filter(s => s.id !== id));
      if (activeStrategy?.id === id) {
        setActiveStrategy(null);
        setActiveResult(null);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const addCondition = (type: 'entry' | 'exit') => {
    const newCond = { indicator: 'RSI', operator: '<', value: 0, timeperiod: 14 };
    if (type === 'entry') setEntryConds([...entryConds, newCond]);
    else setExitConds([...exitConds, newCond]);
  };

  const removeCondition = (type: 'entry' | 'exit', index: number) => {
    if (type === 'entry') setEntryConds(entryConds.filter((_, i) => i !== index));
    else setExitConds(exitConds.filter((_, i) => i !== index));
  };

  const updateCondition = (type: 'entry' | 'exit', index: number, field: string, val: any) => {
    if (type === 'entry') {
      const updated = [...entryConds];
      updated[index] = { ...updated[index], [field]: val };
      setEntryConds(updated);
    } else {
      const updated = [...exitConds];
      updated[index] = { ...updated[index], [field]: val };
      setExitConds(updated);
    }
  };

  const renderConditionBuilder = (type: 'entry' | 'exit', conds: StrategyCondition[]) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', background: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)' }}>
      <h3 style={{ fontSize: '16px', color: type === 'entry' ? 'var(--profit)' : 'var(--loss)' }}>
        {type === 'entry' ? 'Buy Conditions (AND)' : 'Sell Conditions (AND)'}
      </h3>
      {conds.map((c, i) => (
        <div key={i} style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <select className="input-field" value={c.indicator} onChange={e => updateCondition(type, i, 'indicator', e.target.value)} style={{ flex: 1 }}>
            <option value="RSI">RSI</option>
            <option value="MACD">MACD</option>
            <option value="EMA">EMA</option>
            <option value="SMA">SMA</option>
            <option value="VWAP">VWAP</option>
            <option value="Bollinger Bands">Bollinger Bands</option>
          </select>
          <select className="input-field" value={c.operator} onChange={e => updateCondition(type, i, 'operator', e.target.value)} style={{ width: '80px' }}>
            <option value="<">{'<'}</option>
            <option value=">">{'>'}</option>
            <option value="==">==</option>
            <option value="<=">{'<='}</option>
            <option value=">=">{'>='}</option>
          </select>
          <input type="number" className="input-field" value={c.value} onChange={e => updateCondition(type, i, 'value', parseFloat(e.target.value))} style={{ width: '100px' }} placeholder="Value" />
          <input type="number" className="input-field" value={c.timeperiod || 14} onChange={e => updateCondition(type, i, 'timeperiod', parseInt(e.target.value))} style={{ width: '80px' }} placeholder="Period" title="Timeperiod" />
          <button onClick={() => removeCondition(type, i)} style={{ background: 'none', border: 'none', color: 'var(--loss)', cursor: 'pointer' }}><Trash2 size={16} /></button>
        </div>
      ))}
      <button onClick={() => addCondition(type)} className="btn-secondary" style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: '4px', padding: '6px 12px', fontSize: '12px' }}>
        <Plus size={14} /> Add Condition
      </button>
    </div>
  );

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <NavBar />
      
      <div className="page-container animate-fade-in" style={{ flex: 1, display: 'flex', gap: '24px', paddingBottom: '48px' }}>
        {/* Sidebar */}
        <div style={{ width: '280px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <button 
            onClick={() => { setShowBuilder(true); setActiveStrategy(null); setActiveResult(null); }}
            className="btn-primary" 
            style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
          >
            <Plus size={18} /> New Strategy
          </button>
          
          <div className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '8px', minHeight: '300px' }}>
            <h3 style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px', textTransform: 'uppercase' }}>Saved Strategies</h3>
            {loading ? (
              <Activity className="animate-spin" size={20} color="var(--accent-blue)" style={{ alignSelf: 'center', margin: '20px' }} />
            ) : strategies.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', textAlign: 'center', margin: '20px 0' }}>No strategies found.</p>
            ) : (
              strategies.map(s => (
                <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button
                    onClick={() => handleSelectStrategy(s)}
                    style={{
                      flex: 1, padding: '12px', borderRadius: '8px', border: 'none', cursor: 'pointer', textAlign: 'left',
                      background: activeStrategy?.id === s.id ? 'var(--accent-blue)' : 'rgba(255,255,255,0.05)',
                      color: '#fff', transition: 'background 0.2s'
                    }}
                  >
                    <div style={{ fontWeight: 600, fontSize: '14px', marginBottom: '4px' }}>{s.name}</div>
                    <div style={{ fontSize: '12px', opacity: 0.8 }}>{s.symbol} • {s.timeframe}</div>
                  </button>
                  <button onClick={() => handleDeleteStrategy(s.id)} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '8px' }}>
                    <Trash2 size={16} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
        
        {/* Main Content */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {showBuilder ? (
            <div className="glass-panel animate-fade-in" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                <Settings size={24} color="var(--accent-blue)" />
                <h2 style={{ fontSize: '24px' }}>Strategy Builder</h2>
              </div>
              
              <div style={{ display: 'flex', gap: '16px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--text-secondary)' }}>Strategy Name</label>
                  <input type="text" className="input-field" value={bName} onChange={e => setBName(e.target.value)} />
                </div>
                <div style={{ width: '120px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--text-secondary)' }}>Symbol</label>
                  <input type="text" className="input-field" value={bSymbol} onChange={e => setBSymbol(e.target.value.toUpperCase())} />
                </div>
                <div style={{ width: '120px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--text-secondary)' }}>Timeframe</label>
                  <select className="input-field" value={bTimeframe} onChange={e => setBTimeframe(e.target.value)}>
                    <option value="1d">1 Day</option>
                    <option value="1wk">1 Week</option>
                  </select>
                </div>
              </div>
              
              {renderConditionBuilder('entry', entryConds)}
              {renderConditionBuilder('exit', exitConds)}
              
              <button 
                onClick={handleSaveStrategy} 
                disabled={saving}
                className="btn-primary" 
                style={{ alignSelf: 'flex-end', marginTop: '16px' }}
              >
                {saving ? 'Saving...' : 'Save Strategy'}
              </button>
            </div>
          ) : activeStrategy ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div className="glass-panel animate-fade-in" style={{ padding: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h2 style={{ fontSize: '28px', marginBottom: '4px' }}>{activeStrategy.name}</h2>
                  <p style={{ color: 'var(--text-secondary)' }}>{activeStrategy.symbol} • {activeStrategy.timeframe}</p>
                </div>
                <button onClick={handleRunBacktest} disabled={runningTest} className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {runningTest ? <Activity className="animate-spin" size={18} /> : <Play size={18} />}
                  Run Backtest (1 Year)
                </button>
              </div>

              {activeResult && (
                <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                  {/* Metrics */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
                    <div className="glass-panel" style={{ padding: '24px' }}>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '8px' }}>Total Return</div>
                      <div style={{ fontSize: '32px', fontWeight: 600, color: activeResult.total_return >= 0 ? 'var(--profit)' : 'var(--loss)' }}>
                        {activeResult.total_return >= 0 ? '+' : ''}{activeResult.total_return.toFixed(2)}%
                      </div>
                    </div>
                    <div className="glass-panel" style={{ padding: '24px' }}>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '8px' }}>Win Rate</div>
                      <div style={{ fontSize: '32px', fontWeight: 600 }}>
                        {activeResult.win_rate.toFixed(1)}%
                      </div>
                    </div>
                    <div className="glass-panel" style={{ padding: '24px' }}>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '8px' }}>Max Drawdown</div>
                      <div style={{ fontSize: '32px', fontWeight: 600, color: 'var(--loss)' }}>
                        -{activeResult.max_drawdown.toFixed(2)}%
                      </div>
                    </div>
                  </div>

                  {/* Equity Curve approx (Actually just showing cumulative trades) */}
                  <div className="glass-panel" style={{ padding: '24px', height: '400px' }}>
                    <h3 style={{ fontSize: '16px', marginBottom: '24px' }}>Historical Trades & Price</h3>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={activeResult.trades}>
                        <XAxis dataKey="date" stroke="var(--text-secondary)" fontSize={12} />
                        <YAxis domain={['auto', 'auto']} stroke="var(--text-secondary)" fontSize={12} tickFormatter={v => `$${v}`} />
                        <Tooltip 
                          contentStyle={{ background: '#1e1e1e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                          labelStyle={{ color: 'var(--text-secondary)' }}
                        />
                        <Line type="stepAfter" dataKey="price" stroke="var(--accent-blue)" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Trade Log */}
                  <div className="glass-panel" style={{ padding: '24px', overflowX: 'auto' }}>
                    <h3 style={{ fontSize: '16px', marginBottom: '24px' }}>Trade Log</h3>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                          <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Date</th>
                          <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Type</th>
                          <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Price</th>
                          <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Shares</th>
                          <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Total Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {activeResult.trades.length === 0 && (
                          <tr><td colSpan={5} style={{ padding: '32px', textAlign: 'center', color: 'var(--text-secondary)' }}>No trades executed for this period.</td></tr>
                        )}
                        {activeResult.trades.map((t, i) => (
                          <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                            <td style={{ padding: '16px' }}>{t.date}</td>
                            <td style={{ padding: '16px', color: t.type === 'Buy' ? 'var(--profit)' : 'var(--loss)', fontWeight: 600 }}>{t.type}</td>
                            <td style={{ padding: '16px' }}>${t.price.toFixed(2)}</td>
                            <td style={{ padding: '16px' }}>{t.shares}</td>
                            <td style={{ padding: '16px' }}>${(t.price * t.shares).toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                </div>
              )}

            </div>
          ) : (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)', padding: '64px' }}>
              <Zap size={64} style={{ marginBottom: '24px', opacity: 0.5 }} />
              <h2 style={{ fontSize: '24px', marginBottom: '8px' }}>AI Strategy Builder</h2>
              <p style={{ textAlign: 'center', maxWidth: '400px', lineHeight: '1.6' }}>
                Select an existing strategy from the sidebar, or create a new one to test mathematical trading rules against historical market data.
              </p>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};
