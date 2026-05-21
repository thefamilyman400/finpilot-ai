import type { ReactNode } from 'react';
import Sidebar from './Sidebar';
import ChatAssistant from './ChatAssistantWithCalculators';

interface MainLayoutProps {
  children: ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'rgb(249 250 251)' }}>
      {/* Left Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <main
        style={{
          flex: 1,
          marginLeft: '240px',
          marginRight: '360px',
          padding: '2rem',
          overflowY: 'auto',
        }}
      >
        {children}
      </main>

      {/* Right Chat Assistant with Calculators */}
      <ChatAssistant />
    </div>
  );
}

// Made with Bob
