import React from 'react';
import ChatInterfaceWrapper from './ChatInterface';
import { DarkModeProvider } from './context/DarkModeContext'; // ✅ import the provider

function Layout({ children }) {
  return (
    <div style={{ width: '100vw', height: '100vh', background: '#f5f5f5' }}>
      {children}
    </div>
  );
}

function App() {
  return (
    <DarkModeProvider> {/* ✅ wrap your app in DarkModeProvider */}
      <Layout>
        <ChatInterfaceWrapper />
      </Layout>
    </DarkModeProvider>
  );
}

export default App;





