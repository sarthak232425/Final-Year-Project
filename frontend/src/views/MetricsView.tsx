import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { ClusteringMetrics } from '../types';

export const MetricsView: React.FC = () => {
  const [metrics, setMetrics] = useState<ClusteringMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getMetrics();
      setMetrics(res);
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : 'Metrics not available. Run RFM analysis first.'
      );
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-body">
        <div className="loading-overlay">
          <div className="spinner"></div>
          <span>Loading clustering evaluation metrics...</span>
        </div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="page-body">
        <div className="empty-state card">
          <span className="empty-icon">📈</span>
          <h3>Clustering Metrics Unavailable</h3>
          <p>{error || 'Please run the analysis pipeline from the Ingestion tab first.'}</p>
          <button className="btn btn-primary mt-4" onClick={fetchMetrics}>
            🔄 Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-body">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h2>Unsupervised Model Evaluation & Validation</h2>
          <p>
            Statistical validity metrics for K-Means clustering (Random Seed: {metrics.random_seed})
          </p>
        </div>
        <button className="btn btn-secondary" onClick={fetchMetrics}>
          🔄 Refresh Metrics
        </button>
      </div>

      {/* Core Evaluation Metrics */}
      <div className="metric-grid">
        <div className="metric-card">
          <div className="metric-label">Optimal Cluster Count (K)</div>
          <div className="metric-value primary">{metrics.selected_k}</div>
          <div className="metric-sub">Determined by Silhouette maximisation</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Silhouette Score</div>
          <div className="metric-value success">
            {metrics.silhouette_score !== null ? metrics.silhouette_score.toFixed(4) : 'N/A'}
          </div>
          <div className="metric-sub">Range [-1, +1] • Higher is better</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Davies–Bouldin Index</div>
          <div className="metric-value warning">
            {metrics.davies_bouldin_index !== null
              ? metrics.davies_bouldin_index.toFixed(4)
              : 'N/A'}
          </div>
          <div className="metric-sub">Range [0, +∞) • Lower is better</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Calinski–Harabasz Index</div>
          <div className="metric-value accent">
            {metrics.calinski_harabasz_score !== null
              ? metrics.calinski_harabasz_score.toFixed(2)
              : 'N/A'}
          </div>
          <div className="metric-sub">Variance ratio criterion • Higher is better</div>
        </div>
      </div>

      {/* K Sweep Evaluation Chart / Table */}
      <div className="grid-2 mb-8">
        <div className="card">
          <div className="card-header">
            <div className="card-title">K Selection Sweep (K = 2 .. 10)</div>
            <span className="badge badge-primary">Silhouette Profile</span>
          </div>

          <div style={{ height: '220px', display: 'flex', alignItems: 'flex-end', gap: '12px', padding: '16px 0' }}>
            {metrics.k_evaluation.map((evalItem) => {
              const val = evalItem.silhouette ?? 0;
              // Normalize silhouette from -0.2 .. 0.8 to height percentage
              const heightPct = Math.max(10, Math.min(100, ((val + 0.2) / 1.0) * 100));
              const isSelected = evalItem.k === metrics.selected_k;

              return (
                <div
                  key={evalItem.k}
                  style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    height: '100%',
                    justifyContent: 'flex-end',
                  }}
                >
                  <span
                    style={{
                      fontSize: '0.65rem',
                      color: isSelected ? 'var(--color-primary-light)' : 'var(--color-text-muted)',
                      fontWeight: isSelected ? 'bold' : 'normal',
                      marginBottom: '4px',
                    }}
                  >
                    {val.toFixed(2)}
                  </span>
                  <div
                    style={{
                      width: '100%',
                      maxWidth: '32px',
                      height: `${heightPct}%`,
                      backgroundColor: isSelected ? 'var(--color-primary)' : 'var(--color-surface-2)',
                      border: isSelected
                        ? '1px solid var(--color-primary-light)'
                        : '1px solid var(--color-border)',
                      borderRadius: '4px 4px 0 0',
                      transition: 'all var(--transition-base)',
                    }}
                  ></div>
                  <span
                    style={{
                      fontSize: 'var(--font-size-xs)',
                      marginTop: '6px',
                      fontWeight: isSelected ? 700 : 400,
                      color: isSelected ? 'var(--color-text-primary)' : 'var(--color-text-muted)',
                    }}
                  >
                    K={evalItem.k}
                  </span>
                </div>
              );
            })}
          </div>
          <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', textAlign: 'center' }}>
            Highlighted bar indicates selected cluster count K={metrics.selected_k} with maximum separation.
          </p>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title">Mathematical Rigour & Metric Interpretation</div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: 'var(--font-size-sm)' }}>
            <div>
              <strong style={{ color: 'var(--color-primary-light)' }}>1. Silhouette Coefficient:</strong>
              <p style={{ fontSize: 'var(--font-size-xs)', marginTop: '2px' }}>
                Measures how similar an entity is to its own cluster compared to other clusters:
                <br />
                <span className="mono">s = (b - a) / max(a, b)</span>
                <br />
                A score &gt; 0.40 demonstrates cohesive and well-separated customer behavior clusters.
              </p>
            </div>

            <div>
              <strong style={{ color: 'var(--color-warning)' }}>2. Davies–Bouldin Index:</strong>
              <p style={{ fontSize: 'var(--font-size-xs)', marginTop: '2px' }}>
                Evaluates similarity between each cluster and its most similar one. Lower values indicate
                better partition quality with tight within-cluster spread.
              </p>
            </div>

            <div>
              <strong style={{ color: '#a78bfa' }}>3. Calinski–Harabasz (Variance Ratio):</strong>
              <p style={{ fontSize: 'var(--font-size-xs)', marginTop: '2px' }}>
                Ratio of between-clusters dispersion to within-cluster dispersion. Higher values support
                distinct separation of RFM feature centroids.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
