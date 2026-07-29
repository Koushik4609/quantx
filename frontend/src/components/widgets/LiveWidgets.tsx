import { useEffect, useState } from 'react';
import { WidgetContainer } from './WidgetContainer';
import { getPortfolioHealth, getDailyBrief } from '../../api/dashboard';
import { getPortfolio } from '../../api/trading';
import ReactMarkdown from 'react-markdown';

export const AiHealthWidget = ({ portfolioId }: { portfolioId: string }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!portfolioId) {
      setError("No portfolio connected.");
      setLoading(false);
      return;
    }
    getPortfolioHealth(portfolioId)
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [portfolioId]);

  return (
    <WidgetContainer title="AI Portfolio Health" loading={loading} error={error}>
      {data && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ 
              width: '64px', height: '64px', borderRadius: '50%', 
              background: `conic-gradient(var(--accent-blue) ${data.score}%, rgba(255,255,255,0.1) 0)`,
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <div style={{ width: '54px', height: '54px', borderRadius: '50%', background: 'var(--bg-glass)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px', fontWeight: 'bold' }}>
                {data.score}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', color: data.score > 70 ? 'var(--profit)' : data.score > 40 ? 'var(--warning)' : 'var(--loss)' }}>
                {data.health}
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Overall Risk Score</div>
            </div>
          </div>
          <div style={{ fontSize: '14px', lineHeight: '1.5', color: 'var(--text-secondary)' }}>
            {data.analysis}
          </div>
        </div>
      )}
    </WidgetContainer>
  );
};

export const AiDailyBriefWidget = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDailyBrief()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <WidgetContainer title="AI Daily Brief" loading={loading} error={error}>
      {data && (
        <div style={{ fontSize: '14px', lineHeight: '1.6', color: 'var(--text-primary)' }}>
          <ReactMarkdown>{data.brief || data.analysis || "No brief available."}</ReactMarkdown>
        </div>
      )}
    </WidgetContainer>
  );
};

export const PortfolioSummaryWidget = ({ portfolioId }: { portfolioId: string }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!portfolioId) {
      setError("No portfolio connected.");
      setLoading(false);
      return;
    }
    // Provide empty current_prices for now. 
    // In a real app, we'd fetch live quotes first, then pass them in.
    getPortfolio(portfolioId, {})
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [portfolioId]);

  return (
    <WidgetContainer title="Portfolio Value" loading={loading} error={error}>
      {data && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ fontSize: '32px', fontWeight: 'bold' }}>
            ${data.total_equity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div style={{ display: 'flex', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Buying Power</div>
              <div style={{ fontSize: '16px', fontWeight: '500' }}>${data.cash_balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Unrealized PnL</div>
              <div style={{ fontSize: '16px', fontWeight: '500', color: data.total_unrealized_pnl >= 0 ? 'var(--profit)' : 'var(--loss)' }}>
                {data.total_unrealized_pnl >= 0 ? '+' : ''}${data.total_unrealized_pnl.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            </div>
          </div>
        </div>
      )}
    </WidgetContainer>
  );
};

export const AllocationWidget = ({ portfolioId }: { portfolioId: string }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!portfolioId) {
      setError("No portfolio connected.");
      setLoading(false);
      return;
    }
    getPortfolio(portfolioId, {})
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [portfolioId]);

  return (
    <WidgetContainer title="Asset Allocation" loading={loading} error={error} empty={data?.positions?.length === 0} emptyMessage="No active positions to allocate.">
      {data && data.positions && data.positions.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {data.positions.map((pos: any, idx: number) => {
            const value = pos.quantity * pos.current_price;
            const percent = ((value / data.total_equity) * 100).toFixed(1);
            return (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                <div style={{ fontWeight: '500' }}>{pos.symbol}</div>
                <div style={{ color: 'var(--text-secondary)' }}>{percent}%</div>
              </div>
            );
          })}
        </div>
      )}
    </WidgetContainer>
  );
};
