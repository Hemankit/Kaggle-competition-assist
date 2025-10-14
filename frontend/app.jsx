// src/App.jsx
import React from 'react';
import ChatInterfaceWrapper from './ChatInterface';
import { DarkModeProvider } from './context/DarkModeContext';
import { ChatProvider } from './context/ChatContext';

// ✅ Layout Component (full-page container)
function Layout({ children }) {
  return (
    <div
      style={{
        width: '100vw',
        height: '100vh',
        background: '#f5f5f5',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {children}
    </div>
  );
}

function App() {
  return (
    <DarkModeProvider>
      <ChatProvider> {/* ✅ Chat state is now available everywhere */}
        <Layout>
          <ChatInterfaceWrapper />
        </Layout>
      </ChatProvider>
    </DarkModeProvider>
  );
}

export default App;



