import React from 'react';

function Header({ sessionInfo, onLogout, darkMode, onToggleDarkMode }) {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 32px',
      background: darkMode ? '#222' : '#f5f5f5',
      color: darkMode ? '#fff' : '#222',
      borderBottom: darkMode ? '1px solid #333' : '1px solid #e0e0e0',
      boxShadow: '0 2px 4px rgba(0,0,0,0.04)'
    }}>
      <div style={{ fontWeight: 700, fontSize: '1.5em', letterSpacing: '0.5px' }}>
        Kaggle Copilot Assist
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
        {/* Session info */}
        <div style={{ fontSize: '1em', color: darkMode ? '#bbb' : '#555' }}>
          {sessionInfo || 'Session: Guest'}
        </div>
        {/* User menu / logout placeholder */}
        <button
          style={{
            background: 'none',
            border: 'none',
            color: darkMode ? '#fff' : '#222',
            fontSize: '1.2em',
            cursor: 'pointer',
            marginRight: '8px'
          }}
          title="User menu / Logout"
          onClick={onLogout}
        >
          <span role="img" aria-label="user">👤</span>
        </button>
        {/* Dark mode toggle */}
        <button
          onClick={onToggleDarkMode}
          style={{
            background: darkMode ? '#444' : '#eee',
            border: 'none',
            borderRadius: '16px',
            padding: '6px 16px',
            color: darkMode ? '#fff' : '#222',
            cursor: 'pointer',
            fontSize: '1em'
          }}
        >
          {darkMode ? '🌙 Dark' : '☀️ Light'}
        </button>
      </div>
    </header>
  );
}

export default Header;
