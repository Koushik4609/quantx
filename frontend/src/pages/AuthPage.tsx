import React, { useState } from 'react';
import { login, signup, getMe } from '../api/auth';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Activity } from 'lucide-react';

export const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { setToken } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let data;
      if (isLogin) {
        data = await login(email, password);
      } else {
        data = await signup(email, password);
      }
      
      const token = data?.idToken;
      if (token) {
        // We set token explicitly here so getMe() works immediately, 
        // even before onAuthStateChanged resolves.
        setToken(token); 
        const meData = await getMe();
        if (meData) {
          localStorage.setItem('user_id', meData.user_id);
          localStorage.setItem('portfolio_id', meData.portfolio_id);
        }
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  const handleBypass = () => {
    setToken('dev-mock-token');
    localStorage.setItem('user_id', '00000000-0000-0000-0000-000000000000');
    localStorage.setItem('portfolio_id', '00000000-0000-0000-0000-000000000000');
    navigate('/dashboard');
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
      <div className="glass-panel animate-fade-in" style={{ width: '100%', maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '32px' }}>
        
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
          <div style={{ background: 'var(--accent-blue)', padding: '16px', borderRadius: '16px', boxShadow: '0 8px 32px var(--accent-blue-glow)' }}>
            <Activity size={32} color="white" />
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 600 }}>QuantX AI</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            {isLogin ? 'Welcome back to your terminal.' : 'Initialize your trading engine.'}
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label className="input-label">Email</label>
            <input 
              type="email" 
              className="input-field" 
              placeholder="trader@quantx.ai"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          
          <div>
            <label className="input-label">Password</label>
            <input 
              type="password" 
              className="input-field" 
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <div style={{ color: 'var(--loss)', fontSize: '13px', textAlign: 'center', padding: '8px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '6px' }}>
              {error}
            </div>
          )}

          <button type="submit" className="btn-primary" style={{ marginTop: '8px' }} disabled={loading}>
            {loading ? 'Authenticating...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <div style={{ textAlign: 'center', fontSize: '13px', color: 'var(--text-secondary)' }}>
          {isLogin ? "Don't have an account? " : "Already initialized? "}
          <button 
            type="button" 
            onClick={() => setIsLogin(!isLogin)}
            style={{ color: 'var(--accent-blue)', fontWeight: 500 }}
          >
            {isLogin ? 'Sign up' : 'Log in'}
          </button>
        </div>

        <button 
          type="button" 
          onClick={handleBypass}
          style={{ marginTop: '-16px', color: 'var(--warning)', fontSize: '12px', background: 'transparent', border: '1px solid rgba(245, 158, 11, 0.3)', padding: '8px', borderRadius: '6px' }}
        >
          Bypass Login (Dev Mode)
        </button>

      </div>
    </div>
  );
};
