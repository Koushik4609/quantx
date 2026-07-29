import React, { useState } from 'react';
import { NavBar } from '../components/NavBar';
import { buyOrder, sellOrder } from '../api/trading';
import { searchSymbol, getQuote } from '../api/market';
import { AlertCircle, Search, Activity, ArrowRightLeft } from 'lucide-react';

export const TradePage: React.FC = () => {
  const [symbol, setSymbol] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [price, setPrice] = useState<number | ''>('');
  
  const [marketError, setMarketError] = useState('');
  const [marketLoading, setMarketLoading] = useState(false);
  const [quoteData, setQuoteData] = useState<any>(null);

  const [tradeError, setTradeError] = useState('');
  const [tradeSuccess, setTradeSuccess] = useState('');
  const [tradeLoading, setTradeLoading] = useState(false);

  const portfolioId = localStorage.getItem('portfolio_id');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol) return;
    
    setMarketLoading(true);
    setMarketError('');
    setQuoteData(null);
    setPrice('');
    
    try {
      // First try to search, then get quote.
      const result = await searchSymbol(symbol);
      
      // If we got here, maybe the endpoint worked (unlikely per instructions)
      // We will also try to fetch the quote
      const quote = await getQuote(symbol);
      setQuoteData(quote || result);
      
      // If quote API worked, pre-fill price
      if (quote?.last_price) {
        setPrice(quote.last_price);
      }
    } catch (err: any) {
      setMarketError(err.message || 'Market Data Connection Failed. Upstox returned an error.');
    } finally {
      setMarketLoading(false);
    }
  };

  const handleTrade = async (side: 'BUY' | 'SELL') => {
    if (!portfolioId) {
      setTradeError('Portfolio ID missing. Please connect your portfolio in the Dashboard.');
      return;
    }
    if (!symbol || !quantity || !price) {
      setTradeError('Please fill in all fields (Symbol, Quantity, Price).');
      return;
    }

    setTradeLoading(true);
    setTradeError('');
    setTradeSuccess('');

    try {
      if (side === 'BUY') {
        await buyOrder(portfolioId, symbol, Number(quantity), Number(price));
        setTradeSuccess(`Successfully BOUGHT ${quantity} ${symbol} @ $${price}`);
      } else {
        await sellOrder(portfolioId, symbol, Number(quantity), Number(price));
        setTradeSuccess(`Successfully SOLD ${quantity} ${symbol} @ $${price}`);
      }
    } catch (err: any) {
      setTradeError(err.message);
    } finally {
      setTradeLoading(false);
    }
  };

  return (
    <div>
      <NavBar />
      <div className="page-container animate-fade-in">
        <h1 style={{ fontSize: '28px', marginBottom: '8px' }}>Trade Terminal</h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>Execute paper trades and monitor market data.</p>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
          
          {/* Left Column: Market Data Explorer */}
          <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <h2 style={{ fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={20} color="var(--accent-blue)" />
              Market Explorer
            </h2>
            
            <form onSubmit={handleSearch} style={{ display: 'flex', gap: '12px' }}>
              <input 
                type="text" 
                className="input-field" 
                placeholder="Search Symbol (e.g. AAPL)"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              />
              <button type="submit" className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Search size={16} />
                Search
              </button>
            </form>

            {marketLoading && <p style={{ color: 'var(--text-secondary)' }}>Querying upstream market data...</p>}

            {marketError && (
              <div className="error-boundary animate-fade-in">
                <AlertCircle size={24} />
                <span style={{ fontWeight: 600 }}>Upstream API Error</span>
                <span style={{ fontSize: '14px' }}>{marketError}</span>
                <p style={{ fontSize: '12px', opacity: 0.8, marginTop: '8px' }}>
                  No mock data is generated. Please provide valid Upstox credentials in the backend.
                </p>
              </div>
            )}

            {quoteData && (
              <div className="glass-panel animate-fade-in" style={{ background: 'rgba(255,255,255,0.02)' }}>
                <pre style={{ fontSize: '12px', color: 'var(--profit)', overflowX: 'auto' }}>
                  {JSON.stringify(quoteData, null, 2)}
                </pre>
              </div>
            )}

          </div>

          {/* Right Column: Execution */}
          <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <h2 style={{ fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ArrowRightLeft size={20} color="var(--accent-blue)" />
              Order Execution
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label className="input-label">Symbol</label>
                <input 
                  type="text" 
                  className="input-field" 
                  placeholder="AAPL"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label className="input-label">Quantity</label>
                  <input 
                    type="number" 
                    min="0.01"
                    step="0.01"
                    className="input-field" 
                    value={quantity}
                    onChange={(e) => setQuantity(Number(e.target.value))}
                  />
                </div>
                <div>
                  <label className="input-label">Execution Price ($)</label>
                  <input 
                    type="number" 
                    step="0.01"
                    className="input-field" 
                    placeholder="Enter manual price"
                    value={price}
                    onChange={(e) => setPrice(Number(e.target.value))}
                  />
                </div>
              </div>

              {tradeError && (
                <div style={{ color: 'var(--loss)', fontSize: '13px', padding: '12px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '6px' }}>
                  {tradeError}
                </div>
              )}

              {tradeSuccess && (
                <div style={{ color: 'var(--profit)', fontSize: '13px', padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '6px' }}>
                  {tradeSuccess}
                </div>
              )}

              <div style={{ display: 'flex', gap: '16px', marginTop: '8px' }}>
                <button 
                  className="btn-primary" 
                  style={{ flex: 1, background: 'var(--profit)', boxShadow: '0 4px 14px rgba(16, 185, 129, 0.3)' }}
                  onClick={() => handleTrade('BUY')}
                  disabled={tradeLoading}
                >
                  {tradeLoading ? 'Executing...' : 'BUY (Limit)'}
                </button>
                <button 
                  className="btn-primary" 
                  style={{ flex: 1, background: 'var(--loss)', boxShadow: '0 4px 14px rgba(239, 68, 68, 0.3)' }}
                  onClick={() => handleTrade('SELL')}
                  disabled={tradeLoading}
                >
                  {tradeLoading ? 'Executing...' : 'SELL (Limit)'}
                </button>
              </div>

            </div>
          </div>

        </div>
      </div>
    </div>
  );
};
