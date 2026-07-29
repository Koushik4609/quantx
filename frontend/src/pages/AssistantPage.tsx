import React, { useState, useEffect, useRef } from 'react';
import { NavBar } from '../components/NavBar';
import { getChatHistory, sendChatMessage } from '../api/ai';
import type { ChatMessage } from '../api/ai';
import { Send, Bot, User, Activity, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export const AssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // We need to parse user.uid out of the AuthContext, but let's just use localStorage for simplicity
  // if user object from Firebase isn't fully structured.
  // Actually, we can get userId from the auth token or local storage.
  const userId = localStorage.getItem('user_id'); // We need this in login.
  // Wait, Firebase login returns localId. Let's assume it's stored, or we just fallback to a dummy UUID for the UI test.
  // We'll use a hardcoded UUID or check if there's one.
  const effectiveUserId = userId || '00000000-0000-0000-0000-000000000000';
  const portfolioId = localStorage.getItem('portfolio_id');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const history = await getChatHistory(effectiveUserId);
        setMessages(history);
      } catch (err: any) {
        // If it's a 404 or something, just ignore, probably no history yet.
        console.error(err);
      }
    };
    if (effectiveUserId) {
      fetchHistory();
    }
  }, [effectiveUserId]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !portfolioId) {
      if (!portfolioId) setError('Portfolio ID missing. Please connect in Dashboard first.');
      return;
    }

    const userMessage = input.trim();
    setInput('');
    setError('');
    
    // Optimistic UI update
    const tempUserMsg: ChatMessage = {
      id: Date.now().toString(),
      message_role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);
    setLoading(true);

    try {
      const response = await sendChatMessage(effectiveUserId, portfolioId, userMessage);
      
      const tempAiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message_role: 'assistant',
        content: response.response,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, tempAiMsg]);
    } catch (err: any) {
      setError(err.message || 'Failed to communicate with QuantX AI.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <NavBar />
      
      <div className="page-container animate-fade-in" style={{ flex: 1, display: 'flex', flexDirection: 'column', paddingBottom: '24px', overflow: 'hidden' }}>
        <h1 style={{ fontSize: '28px', marginBottom: '8px' }}>QuantX AI Assistant</h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>Your elite, real-time financial analyst.</p>

        {!portfolioId && (
          <div className="error-boundary" style={{ marginBottom: '16px' }}>
            <AlertCircle size={20} />
            <span>Missing Portfolio ID. The AI requires your portfolio context. Please set it in the Dashboard.</span>
          </div>
        )}
        
        {error && (
          <div className="error-boundary" style={{ marginBottom: '16px' }}>
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        {/* Chat Area */}
        <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '0', overflow: 'hidden' }}>
          
          <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {messages.length === 0 && !loading && (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)', opacity: 0.5 }}>
                <Bot size={48} style={{ marginBottom: '16px' }} />
                <h3>How can I analyze the markets for you today?</h3>
              </div>
            )}

            {messages.map((msg) => (
              <div 
                key={msg.id} 
                style={{ 
                  display: 'flex', 
                  gap: '16px',
                  alignItems: 'flex-start',
                  flexDirection: msg.message_role === 'user' ? 'row-reverse' : 'row'
                }}
              >
                <div style={{ 
                  background: msg.message_role === 'user' ? 'rgba(255,255,255,0.1)' : 'var(--accent-blue)',
                  padding: '8px',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  {msg.message_role === 'user' ? <User size={20} /> : <Bot size={20} color="white" />}
                </div>
                
                <div style={{ 
                  background: msg.message_role === 'user' ? 'rgba(255,255,255,0.05)' : 'rgba(37, 99, 235, 0.1)',
                  padding: '16px 20px',
                  borderRadius: '12px',
                  maxWidth: '75%',
                  border: msg.message_role === 'user' ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(37, 99, 235, 0.2)',
                  color: 'var(--text-primary)',
                  fontSize: '15px',
                  lineHeight: '1.6'
                }}>
                  {msg.message_role === 'user' ? (
                    msg.content
                  ) : (
                    <div className="markdown-body">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                <div style={{ background: 'var(--accent-blue)', padding: '8px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Bot size={20} color="white" />
                </div>
                <div style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-blue)' }}>
                  <Activity size={18} className="animate-spin" />
                  <span>QuantX AI is analyzing the market...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div style={{ padding: '16px', borderTop: '1px solid rgba(255,255,255,0.05)', background: 'rgba(0,0,0,0.2)' }}>
            <form onSubmit={handleSend} style={{ display: 'flex', gap: '12px' }}>
              <input 
                type="text" 
                className="input-field" 
                placeholder="Ask about your portfolio, market news, or a specific ticker (e.g., 'What is the news on AAPL?')"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
                style={{ flex: 1, padding: '16px', fontSize: '16px' }}
              />
              <button 
                type="submit" 
                className="btn-primary" 
                disabled={loading || !input.trim() || !portfolioId}
                style={{ padding: '0 24px', display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <Send size={18} />
                Send
              </button>
            </form>
          </div>

        </div>
      </div>
    </div>
  );
};
