import React from 'react';

export type ActiveTab = 'upload' | 'segments' | 'recommendations' | 'metrics';

interface SidebarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  systemHealthy: boolean | null;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  systemHealthy,
}) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h1>SegmentAI</h1>
        <p>Intelligent Retention Platform</p>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-title">Core Pipeline</div>

        <button
          className={`nav-item w-full ${activeTab === 'upload' ? 'active' : ''}`}
          style={{ background: 'none', border: 'none', textAlign: 'left' }}
          onClick={() => setActiveTab('upload')}
        >
          <span className="nav-icon">📤</span>
          <span>Data Ingestion</span>
        </button>

        <button
          className={`nav-item w-full ${activeTab === 'segments' ? 'active' : ''}`}
          style={{ background: 'none', border: 'none', textAlign: 'left' }}
          onClick={() => setActiveTab('segments')}
        >
          <span className="nav-icon">👥</span>
          <span>RFM & Segments</span>
        </button>

        <button
          className={`nav-item w-full ${activeTab === 'recommendations' ? 'active' : ''}`}
          style={{ background: 'none', border: 'none', textAlign: 'left' }}
          onClick={() => setActiveTab('recommendations')}
        >
          <span className="nav-icon">🎯</span>
          <span>Recommendations</span>
        </button>

        <div className="nav-section-title">Validation & Research</div>

        <button
          className={`nav-item w-full ${activeTab === 'metrics' ? 'active' : ''}`}
          style={{ background: 'none', border: 'none', textAlign: 'left' }}
          onClick={() => setActiveTab('metrics')}
        >
          <span className="nav-icon">📈</span>
          <span>Model Metrics</span>
        </button>
      </nav>

      {/* System Status in Sidebar Footer */}
      <div
        style={{
          padding: 'var(--space-4) var(--space-6)',
          borderTop: '1px solid var(--color-border)',
          fontSize: 'var(--font-size-xs)',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
        }}
      >
        <div className="flex items-center gap-2">
          <span
            className={`status-dot ${
              systemHealthy === true ? 'green' : systemHealthy === false ? 'red' : 'amber'
            }`}
          ></span>
          <span style={{ color: 'var(--color-text-secondary)', fontWeight: 600 }}>
            {systemHealthy === true
              ? 'Backend API Online'
              : systemHealthy === false
              ? 'Backend Offline'
              : 'Checking API...'}
          </span>
        </div>
        <div style={{ color: 'var(--color-text-muted)' }}>
          Review Milestone: Oct 2026
        </div>
      </div>
    </aside>
  );
};
