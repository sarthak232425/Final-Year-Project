import React, { useState, useEffect } from 'react';
import { Sidebar, ActiveTab } from './components/Sidebar';
import { UploadView } from './views/UploadView';
import { SegmentsView } from './views/SegmentsView';
import { RecommendationsView } from './views/RecommendationsView';
import { MetricsView } from './views/MetricsView';
import { api } from './api/client';
import { CleaningSummary } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('upload');
  const [systemHealthy, setSystemHealthy] = useState<boolean | null>(null);
  const [cleaningSummary, setCleaningSummary] = useState<CleaningSummary | null>(null);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      await api.health();
      setSystemHealthy(true);
    } catch {
      setSystemHealthy(false);
    }
  };

  const handleAnalysisComplete = () => {
    setActiveTab('segments');
  };

  return (
    <div className="app-container">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemHealthy={systemHealthy}
      />

      <main className="main-content">
        <header className="page-header flex justify-between items-center">
          <div>
            <h2>
              {activeTab === 'upload' && 'Data Ingestion & Quality Control'}
              {activeTab === 'segments' && 'Behavioral Segments & RFM Profiling'}
              {activeTab === 'recommendations' && 'Fatigue & WhatsApp Campaign Recommendations'}
              {activeTab === 'metrics' && 'Model Validation & Evaluation Metrics'}
            </h2>
            <p>
              AI-Based Customer Segmentation and WhatsApp Marketing Platform • Final-Year Project
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="simulated-label">Meta WhatsApp Mock Engine</span>
            <div
              className="badge"
              style={{
                backgroundColor: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-secondary)',
              }}
            >
              Seed: 42
            </div>
          </div>
        </header>

        {systemHealthy === false && (
          <div className="api-alert" role="status">
            <strong>Backend API unavailable.</strong>
            <span>Start FastAPI on port 8000 to upload data and run analysis.</span>
          </div>
        )}

        {activeTab === 'upload' && (
          <UploadView
            onAnalysisComplete={handleAnalysisComplete}
            cleaningSummary={cleaningSummary}
            setCleaningSummary={setCleaningSummary}
          />
        )}

        {activeTab === 'segments' && <SegmentsView />}

        {activeTab === 'recommendations' && <RecommendationsView />}

        {activeTab === 'metrics' && <MetricsView />}
      </main>
    </div>
  );
};

export default App;
