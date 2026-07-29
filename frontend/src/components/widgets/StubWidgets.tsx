import { useEffect, useState } from 'react';
import { WidgetContainer } from './WidgetContainer';
import { getMarketMovers, getMarketNews, getMarketSentiment, getEconomicCalendar, getSectorHeatmap } from '../../api/dashboard';

export const MoversWidget = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMarketMovers().catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  return <WidgetContainer title="Top Gainers & Losers" loading={loading} error={error}><div/></WidgetContainer>;
};

export const NewsWidget = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [news, setNews] = useState<any[]>([]);

  useEffect(() => {
    getMarketNews()
      .then(data => setNews(Array.isArray(data) ? data.slice(0, 5) : []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <WidgetContainer title="Latest Market News" loading={loading} error={error}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {news.length === 0 && !loading && !error && <div style={{ color: 'var(--text-secondary)' }}>No news available.</div>}
        {news.map((item, i) => (
          <div key={i} style={{ borderBottom: i !== news.length - 1 ? '1px solid var(--border-color)' : 'none', paddingBottom: i !== news.length - 1 ? '12px' : '0' }}>
            <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-primary)', textDecoration: 'none', fontWeight: 'bold', display: 'block', marginBottom: '4px' }}>
              {item.headline}
            </a>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              {item.source} • {new Date(item.datetime * 1000).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>
    </WidgetContainer>
  );
};

export const SentimentWidget = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMarketSentiment().catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  return <WidgetContainer title="Fear & Greed Index" loading={loading} error={error}><div/></WidgetContainer>;
};

export const CalendarWidget = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    getEconomicCalendar()
      .then(data => setEvents(data?.economicCalendar ? data.economicCalendar.slice(0, 5) : []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <WidgetContainer title="Economic Calendar" loading={loading} error={error}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {events.length === 0 && !loading && !error && <div style={{ color: 'var(--text-secondary)' }}>No calendar events available.</div>}
        {events.map((evt, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: i !== events.length - 1 ? '1px solid var(--border-color)' : 'none', paddingBottom: i !== events.length - 1 ? '8px' : '0' }}>
            <div>
              <div style={{ fontWeight: '500', color: 'var(--text-primary)' }}>{evt.event}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{evt.country}</div>
            </div>
            <div style={{ textAlign: 'right', fontSize: '14px', color: 'var(--text-primary)' }}>
              <div>{evt.actual ? evt.actual : '-'}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Est: {evt.estimate ? evt.estimate : '-'}</div>
            </div>
          </div>
        ))}
      </div>
    </WidgetContainer>
  );
};

export const HeatmapWidget = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSectorHeatmap().catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  return <WidgetContainer title="Sector Heatmap" loading={loading} error={error}><div/></WidgetContainer>;
};
