import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Activity, LogOut } from 'lucide-react';

export const NavBar: React.FC = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="nav-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ background: 'var(--accent-blue)', padding: '8px', borderRadius: '8px', boxShadow: '0 4px 16px var(--accent-blue-glow)' }}>
          <Activity size={20} color="white" />
        </div>
        <span style={{ fontWeight: 700, letterSpacing: '0.5px' }}>QuantX AI</span>
      </div>

      <div className="nav-links">
        <NavLink 
          to="/dashboard" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          Dashboard
        </NavLink>
        <NavLink 
          to="/trade" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          Terminal
        </NavLink>
        <NavLink 
          to="/transactions" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          Ledger
        </NavLink>
        <NavLink 
          to="/assistant" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          AI Assistant
        </NavLink>
        <NavLink 
          to="/news" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          News
        </NavLink>
        <NavLink 
          to="/academy" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          Academy
        </NavLink>
        <NavLink 
          to="/analytics" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          Analytics
        </NavLink>
        <NavLink 
          to="/portfolio-ai" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          Portfolio AI
        </NavLink>
        <NavLink 
          to="/alerts" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          Alerts
        </NavLink>
        <NavLink 
          to="/broker" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          Broker
        </NavLink>
        <NavLink 
          to="/strategies" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          Strategies
        </NavLink>
      </div>

      <button onClick={handleLogout} style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
        <LogOut size={16} />
        <span style={{ fontSize: '14px', fontWeight: 500 }}>Disconnect</span>
      </button>
    </nav>
  );
};
