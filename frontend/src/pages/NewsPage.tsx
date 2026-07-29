import React, { useState, useEffect } from 'react';
import { NavBar } from '../components/NavBar';
import { getMarketNews, getCompanyNews, summarizeArticle, addBookmark, removeBookmark, getBookmarks, type NewsArticle } from '../api/news';
import type { Bookmark } from '../api/news';
import { Search, Bookmark as BookmarkIcon, Sparkles, X, Activity, ExternalLink } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export const NewsPage: React.FC = () => {
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'market' | 'bookmarks'>('market');
  
  // AI Summary Modal State
  const [summaryModalOpen, setSummaryModalOpen] = useState(false);
  const [activeArticle, setActiveArticle] = useState<NewsArticle | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);

  const userId = localStorage.getItem('user_id') || '00000000-0000-0000-0000-000000000000';

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'market') {
        const data = await getMarketNews();
        setNews(data);
      } else {
        const bks = await getBookmarks(userId);
        setBookmarks(bks);
      }
      
      // Always keep bookmarks up to date for the UI toggles
      if (activeTab === 'market') {
          const bks = await getBookmarks(userId);
          setBookmarks(bks);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setActiveTab('market');
      fetchData();
      return;
    }
    
    setLoading(true);
    try {
      const data = await getCompanyNews(searchQuery.trim().toUpperCase());
      setNews(data);
      setActiveTab('market'); // Override to show search results
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const toggleBookmark = async (article: NewsArticle) => {
    const isBookmarked = bookmarks.find(b => b.article_url === article.url);
    try {
      if (isBookmarked) {
        await removeBookmark(isBookmarked.id);
        setBookmarks(prev => prev.filter(b => b.id !== isBookmarked.id));
      } else {
        const newBk = await addBookmark({
          user_id: userId,
          article_url: article.url,
          article_title: article.title,
          source: article.source,
          published_at: article.published_at
        });
        setBookmarks(prev => [newBk, ...prev]);
      }
    } catch (e) {
      console.error("Failed to bookmark", e);
    }
  };

  const openSummary = async (article: NewsArticle) => {
    setActiveArticle(article);
    setSummary(null);
    setSummaryModalOpen(true);
    setSummaryLoading(true);
    try {
      const res = await summarizeArticle(article.url);
      setSummary(res.summary);
    } catch (e: any) {
      setSummary(e.message || "Failed to generate summary.");
    } finally {
      setSummaryLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <NavBar />
      
      <div className="page-container animate-fade-in" style={{ flex: 1, paddingBottom: '48px', display: 'flex', flexDirection: 'column' }}>
        
        {/* Header Area */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
          <div>
            <h1 style={{ fontSize: '28px', marginBottom: '8px' }}>Market Intelligence</h1>
            <p style={{ color: 'var(--text-secondary)' }}>Real-time news with AI-powered summaries.</p>
          </div>
          
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px' }}>
            <div style={{ position: 'relative' }}>
              <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
              <input 
                type="text" 
                className="input-field"
                placeholder="Search ticker (e.g. AAPL)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{ paddingLeft: '40px', width: '250px' }}
              />
            </div>
            <button type="submit" className="btn-primary" style={{ padding: '0 16px' }}>Search</button>
          </form>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '16px' }}>
          <button 
            className={`btn-secondary ${activeTab === 'market' ? 'active' : ''}`}
            onClick={() => setActiveTab('market')}
            style={{ background: activeTab === 'market' ? 'var(--accent-blue)' : 'transparent', border: 'none' }}
          >
            Latest News
          </button>
          <button 
            className={`btn-secondary ${activeTab === 'bookmarks' ? 'active' : ''}`}
            onClick={() => setActiveTab('bookmarks')}
            style={{ background: activeTab === 'bookmarks' ? 'var(--accent-blue)' : 'transparent', border: 'none' }}
          >
            Bookmarks ({bookmarks.length})
          </button>
        </div>

        {/* Content Area */}
        {loading ? (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Activity className="animate-spin" size={32} color="var(--accent-blue)" />
          </div>
        ) : activeTab === 'market' && news.length === 0 ? (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
            No articles found.
          </div>
        ) : activeTab === 'bookmarks' && bookmarks.length === 0 ? (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
            You haven't bookmarked any articles yet.
          </div>
        ) : (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', 
            gap: '24px' 
          }}>
            {/* Render loop */}
            {(activeTab === 'market' ? news : bookmarks).map((item: any) => {
              const isBookmarked = bookmarks.some(b => b.article_url === (item.url || item.article_url));
              // Map between NewsArticle and Bookmark schema
              const title = item.title || item.article_title;
              const source = item.source;
              const url = item.url || item.article_url;
              const pubDate = new Date(item.published_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
              
              return (
                <div key={item.id} className="glass-panel" style={{ display: 'flex', flexDirection: 'column', padding: '20px', gap: '16px', position: 'relative' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '12px', color: 'var(--accent-blue)', fontWeight: 600, background: 'rgba(37, 99, 235, 0.1)', padding: '4px 8px', borderRadius: '4px' }}>
                      {source || 'News'}
                    </span>
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      {pubDate}
                    </span>
                  </div>
                  
                  <h3 style={{ fontSize: '16px', lineHeight: '1.4', fontWeight: 600 }}>
                    <a href={url} target="_blank" rel="noreferrer" style={{ color: 'inherit', textDecoration: 'none' }}>
                      {title}
                    </a>
                  </h3>
                  
                  <div style={{ flex: 1 }}></div>

                  <div style={{ display: 'flex', gap: '8px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '16px' }}>
                    <button 
                      onClick={() => openSummary({ title, source, url, id: item.id, published_at: item.published_at, related_tickers: item.related_tickers || [], summary: '' })}
                      style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', background: 'rgba(168, 85, 247, 0.1)', color: '#c084fc', border: '1px solid rgba(168, 85, 247, 0.2)', padding: '8px', borderRadius: '8px', fontSize: '13px', fontWeight: 500, cursor: 'pointer' }}
                    >
                      <Sparkles size={16} />
                      AI Summary
                    </button>
                    
                    <button 
                      onClick={() => toggleBookmark({ title, source, url, id: item.id, published_at: item.published_at, related_tickers: item.related_tickers || [], summary: '' })}
                      style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', cursor: 'pointer', color: isBookmarked ? 'var(--accent-blue)' : 'var(--text-secondary)' }}
                    >
                      <BookmarkIcon size={18} fill={isBookmarked ? "currentColor" : "none"} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* AI Summary Modal */}
      {summaryModalOpen && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px', background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)' }}>
          <div className="glass-panel animate-fade-in" style={{ width: '100%', maxWidth: '600px', maxHeight: '80vh', display: 'flex', flexDirection: 'column', gap: '24px', position: 'relative' }}>
            <button 
              onClick={() => setSummaryModalOpen(false)}
              style={{ position: 'absolute', top: '16px', right: '16px', background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
            >
              <X size={24} />
            </button>
            
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#c084fc', marginBottom: '8px' }}>
                <Sparkles size={18} />
                <span style={{ fontWeight: 600, fontSize: '14px' }}>AI Summary</span>
              </div>
              <h2 style={{ fontSize: '20px', lineHeight: '1.4', paddingRight: '24px' }}>{activeArticle?.title}</h2>
            </div>
            
            <div style={{ flex: 1, overflowY: 'auto', paddingRight: '8px', color: 'var(--text-primary)', fontSize: '15px', lineHeight: '1.6' }}>
              {summaryLoading ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', padding: '40px 0', color: '#c084fc' }}>
                  <Activity className="animate-spin" size={32} />
                  <span>QuantX AI is reading this article...</span>
                </div>
              ) : (
                <div className="markdown-body">
                  <ReactMarkdown>{summary || ""}</ReactMarkdown>
                </div>
              )}
            </div>
            
            <a 
              href={activeArticle?.url} 
              target="_blank" 
              rel="noreferrer"
              className="btn-secondary" 
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', textDecoration: 'none' }}
            >
              Read Original Source <ExternalLink size={16} />
            </a>
          </div>
        </div>
      )}
    </div>
  );
};
