import React from 'react';
import { NavBar } from '../components/NavBar';
import { PortfolioSummaryWidget, AllocationWidget, AiHealthWidget, AiDailyBriefWidget } from '../components/widgets/LiveWidgets';
import { MarketStatusWidget, WatchlistWidget } from '../components/widgets/MarketWidgets';
import { MoversWidget, NewsWidget, SentimentWidget, CalendarWidget, HeatmapWidget } from '../components/widgets/StubWidgets';

export const DashboardPage: React.FC = () => {
  const portfolioId = localStorage.getItem('portfolio_id') || '';

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <NavBar />
      
      <div className="page-container animate-fade-in" style={{ flex: 1, paddingBottom: '48px' }}>
        <h1 style={{ fontSize: '28px', marginBottom: '8px' }}>Professional Dashboard</h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>Real-time analytics and elite market intelligence.</p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(12, 1fr)',
          gap: '24px',
          gridAutoRows: 'minmax(200px, auto)'
        }}>
          
          {/* Row 1: Core Portfolio metrics */}
          <div style={{ gridColumn: 'span 4' }}>
            <PortfolioSummaryWidget portfolioId={portfolioId} />
          </div>
          <div style={{ gridColumn: 'span 4' }}>
            <AiHealthWidget portfolioId={portfolioId} />
          </div>
          <div style={{ gridColumn: 'span 4' }}>
            <AllocationWidget portfolioId={portfolioId} />
          </div>

          {/* Row 2: AI & Market */}
          <div style={{ gridColumn: 'span 8' }}>
            <AiDailyBriefWidget />
          </div>
          <div style={{ gridColumn: 'span 4' }}>
            <WatchlistWidget />
          </div>

          {/* Row 3: Live Market Data (Upstox Stubs/Errors due to lack of API support) */}
          <div style={{ gridColumn: 'span 4' }}>
            <SentimentWidget />
          </div>
          <div style={{ gridColumn: 'span 4' }}>
            <HeatmapWidget />
          </div>
          <div style={{ gridColumn: 'span 4' }}>
            <MoversWidget />
          </div>

          {/* Row 4: Calendar and News */}
          <div style={{ gridColumn: 'span 6' }}>
            <CalendarWidget />
          </div>
          <div style={{ gridColumn: 'span 6' }}>
            <NewsWidget />
          </div>
          
          {/* Row 5: Market Status */}
          <div style={{ gridColumn: 'span 12' }}>
            <MarketStatusWidget />
          </div>

        </div>
      </div>
    </div>
  );
};
