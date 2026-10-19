import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { SegmentListResponse, RFMResult } from '../types';

interface SegmentsViewProps {
  onSelectCustomerForCampaign?: (customerId: string) => void;
}

export const SegmentsView: React.FC<SegmentsViewProps> = () => {
  const [segmentsData, setSegmentsData] = useState<SegmentListResponse | null>(null);
  const [rfmData, setRfmData] = useState<RFMResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<number | 'all'>('all');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [segRes, rfmRes] = await Promise.all([
        api.getSegments(),
        api.getRFM(1, 100),
      ]);
      setSegmentsData(segRes);
      setRfmData(rfmRes as RFMResult);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch segmentation data. Please run analysis first.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-body">
        <div className="loading-overlay">
          <div className="spinner"></div>
          <span>Loading segmentation and RFM profiles...</span>
        </div>
      </div>
    );
  }

  if (error || !segmentsData) {
    return (
      <div className="page-body">
        <div className="empty-state card">
          <span className="empty-icon">👥</span>
          <h3>No Segmentation Data Available</h3>
          <p>{error || 'Please upload a dataset and run the RFM & Clustering analysis first.'}</p>
          <button className="btn btn-primary mt-4" onClick={fetchData}>
            🔄 Refresh Data
          </button>
        </div>
      </div>
    );
  }

  const filteredCustomers = rfmData?.customers.filter(() => {
    // If filtering by cluster is enabled
    return true;
  }) ?? [];

  return (
    <div className="page-body">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h2>Customer Segmentation & RFM Profiles</h2>
          <p>
            Unsupervised K-Means clustering (K = {segmentsData.selected_k}) with dynamic behavioral labeling
          </p>
        </div>
        <button className="btn btn-secondary" onClick={fetchData}>
          🔄 Refresh
        </button>
      </div>

      {/* Segment Cards */}
      <div className="grid-3 mb-8">
        {segmentsData.segments.map((seg) => (
          <div
            key={seg.cluster_id}
            className={`card ${selectedCluster === seg.cluster_id ? 'active-card' : ''}`}
            style={{
              cursor: 'pointer',
              borderLeft: `4px solid ${
                seg.label.includes('Champion') || seg.label.includes('Loyal')
                  ? 'var(--color-success)'
                  : seg.label.includes('At Risk') || seg.label.includes('Churn')
                  ? 'var(--color-danger)'
                  : 'var(--color-primary)'
              }`,
            }}
            onClick={() =>
              setSelectedCluster(selectedCluster === seg.cluster_id ? 'all' : seg.cluster_id)
            }
          >
            <div className="card-header">
              <span className="badge badge-primary">Cluster {seg.cluster_id}</span>
              <span className="badge badge-accent">{seg.size} Customers</span>
            </div>
            <h3 style={{ fontSize: 'var(--font-size-lg)', marginBottom: '8px' }}>{seg.label}</h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: 'var(--font-size-sm)' }}>
              <div className="flex justify-between">
                <span style={{ color: 'var(--color-text-muted)' }}>Median Recency:</span>
                <span className="mono">{seg.median_recency_days} days</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: 'var(--color-text-muted)' }}>Median Frequency:</span>
                <span className="mono">{seg.median_frequency} orders</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: 'var(--color-text-muted)' }}>Median Spend:</span>
                <span className="mono">${seg.median_monetary.toFixed(2)}</span>
              </div>
            </div>

            <div style={{ marginTop: '12px', paddingTop: '8px', borderTop: '1px solid var(--color-border)' }}>
              <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                Sample IDs: {seg.example_customer_ids.slice(0, 3).join(', ')}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* RFM Dataset Level Metrics */}
      {rfmData && (
        <div className="card mb-8">
          <div className="card-header">
            <div className="card-title">Dataset RFM Baseline Medians</div>
            <span className="badge badge-secondary">
              Total Customers: {rfmData.customer_count}
            </span>
          </div>
          <div className="metric-grid">
            <div className="metric-card">
              <div className="metric-label">Dataset Median Recency</div>
              <div className="metric-value primary">{rfmData.dataset_median_recency}d</div>
              <div className="metric-sub">Days since last invoice</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Dataset Median Frequency</div>
              <div className="metric-value accent">{rfmData.dataset_median_frequency}</div>
              <div className="metric-sub">Orders per customer</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Dataset Median Monetary</div>
              <div className="metric-value success">
                ${rfmData.dataset_median_monetary.toFixed(2)}
              </div>
              <div className="metric-sub">Lifetime order value</div>
            </div>
          </div>
        </div>
      )}

      {/* Customer RFM Table */}
      {rfmData && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">Customer RFM Feature Vectors & Scores</div>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Customer ID</th>
                  <th>Recency (Days)</th>
                  <th>Frequency (Invoices)</th>
                  <th>Monetary ($)</th>
                  <th>R-Score</th>
                  <th>F-Score</th>
                  <th>M-Score</th>
                  <th>Composite RFM</th>
                </tr>
              </thead>
              <tbody>
                {filteredCustomers.map((c) => (
                  <tr key={c.customer_id}>
                    <td className="mono">{c.customer_id}</td>
                    <td className="mono">{c.recency_days}</td>
                    <td className="mono">{c.frequency}</td>
                    <td className="mono">${c.monetary.toFixed(2)}</td>
                    <td>
                      <span className="badge badge-primary">{c.r_score}/5</span>
                    </td>
                    <td>
                      <span className="badge badge-accent">{c.f_score}/5</span>
                    </td>
                    <td>
                      <span className="badge badge-success">{c.m_score}/5</span>
                    </td>
                    <td>
                      <strong className="mono" style={{ color: 'var(--color-primary-light)' }}>
                        {c.rfm_score}
                      </strong>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
