import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Recommendation, RecommendationListResponse } from '../types';

export const RecommendationsView: React.FC = () => {
  const [data, setData] = useState<RecommendationListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterEligible, setFilterEligible] = useState<'all' | 'eligible' | 'ineligible'>('all');
  const [previewRec, setPreviewRec] = useState<Recommendation | null>(null);

  useEffect(() => {
    fetchRecommendations();
  }, [filterEligible]);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getRecommendations({
        eligible_only: filterEligible === 'eligible' ? true : undefined,
        page_size: 100,
      });
      setData(res);
    } catch (err: unknown) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to fetch recommendations. Please run RFM analysis first.'
      );
    } finally {
      setLoading(false);
    }
  };

  const getTemplatePreview = (rec: Recommendation) => {
    switch (rec.campaign_type) {
      case 'vip_loyalty':
        return `Hello! As one of our most valued VIP customers, we're pleased to offer you exclusive early access to our seasonal collection. Use code VIPACCESS for 20% off your next purchase. Reply STOP to opt out.`;
      case 'win_back':
        return `We miss you! It's been a while since your last visit. Enjoy 15% off your next order with code WELCOMEBACK. Free shipping on orders over $30. Reply STOP to opt out.`;
      case 'cross_sell':
        return `Thank you for your recent purchase! Based on what you love, we've hand-picked matching essentials tailored for you. Check them out today: https://store.example/foryou. Reply STOP to opt out.`;
      default:
        return `Exclusive update from our store! Check out our new arrivals and special offers just for you. Reply STOP to opt out.`;
    }
  };

  const filteredRecs = data?.recommendations.filter((r) => {
    if (filterEligible === 'eligible') return r.eligible;
    if (filterEligible === 'ineligible') return !r.eligible;
    return true;
  }) ?? [];

  return (
    <div className="page-body">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h2>Campaign Recommendations & Fatigue Engine</h2>
          <p>
            Rule-based campaign matching with strict anti-fatigue, frequency capping, and consent gating
          </p>
        </div>
        <div className="flex gap-2">
          <button
            className={`btn ${filterEligible === 'all' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setFilterEligible('all')}
          >
            All ({data?.total ?? 0})
          </button>
          <button
            className={`btn ${filterEligible === 'eligible' ? 'btn-success' : 'btn-secondary'}`}
            onClick={() => setFilterEligible('eligible')}
          >
            Eligible ({data?.eligible_count ?? 0})
          </button>
          <button
            className={`btn ${filterEligible === 'ineligible' ? 'btn-danger' : 'btn-secondary'}`}
            onClick={() => setFilterEligible('ineligible')}
          >
            Ineligible ({data?.ineligible_count ?? 0})
          </button>
        </div>
      </div>

      {/* Top Level Summary Cards */}
      {data && (
        <div className="metric-grid">
          <div className="metric-card">
            <div className="metric-label">Total Audience</div>
            <div className="metric-value">{data.total}</div>
            <div className="metric-sub">Segmented profiles</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Approved for Outreach</div>
            <div className="metric-value success">{data.eligible_count}</div>
            <div className="metric-sub">Passed all fatigue & consent gates</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Blocked / Fatigued</div>
            <div className="metric-value danger">{data.ineligible_count}</div>
            <div className="metric-sub">Protected by ethical guardrails</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Targeting Efficiency</div>
            <div className="metric-value primary">
              {data.total > 0 ? ((data.eligible_count / data.total) * 100).toFixed(0) : 0}%
            </div>
            <div className="metric-sub">Relevance qualification rate</div>
          </div>
        </div>
      )}

      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <span>Evaluating fatigue rules and generating recommendations...</span>
        </div>
      )}

      {error && (
        <div className="card empty-state">
          <span className="empty-icon">⚠️</span>
          <h3>Recommendations Unavailable</h3>
          <p>{error}</p>
        </div>
      )}

      {/* Recommendations Cards List */}
      {!loading && !error && filteredRecs.length > 0 && (
        <div className="flex flex-col gap-4">
          {filteredRecs.map((rec) => (
            <div
              key={rec.customer_id}
              className={`rec-card ${rec.eligible ? 'eligible' : 'ineligible'}`}
            >
              <div className="rec-card-header">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="rec-customer-id">{rec.customer_id}</span>
                    <span className="badge badge-primary">{rec.segment_label}</span>
                    <span
                      className={`badge ${
                        rec.eligible ? 'badge-success' : 'badge-danger'
                      }`}
                    >
                      {rec.eligible ? '✓ Approved' : '✕ Blocked'}
                    </span>
                    {!rec.eligible && rec.ineligibility_reason && (
                      <span className="badge badge-warning">{rec.ineligibility_reason}</span>
                    )}
                  </div>
                  <h4 style={{ fontSize: 'var(--font-size-base)', fontWeight: 600 }}>
                    {rec.campaign_type_display}
                  </h4>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div className="rec-score">{rec.heuristic_score}</div>
                  <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                    Heuristic Priority
                  </span>
                </div>
              </div>

              {/* Natural Language Explanation */}
              <div className="rec-explanation">
                <strong>Strategy & Rationale:</strong> {rec.explanation}
              </div>

              {/* Supporting Rules Checklist */}
              <div style={{ marginTop: '12px' }}>
                <span
                  style={{
                    fontSize: 'var(--font-size-xs)',
                    fontWeight: 600,
                    color: 'var(--color-text-muted)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}
                >
                  Fatigue & Policy Verifications:
                </span>
                <ul className="check-list">
                  {rec.eligibility_checks.map((chk, idx) => (
                    <li
                      key={idx}
                      className={`check-item ${chk.passed ? 'passed' : 'failed'}`}
                    >
                      <span className="check-icon">{chk.passed ? '●' : '✕'}</span>
                      <span>
                        <strong style={{ color: 'var(--color-text-primary)' }}>{chk.check}:</strong>{' '}
                        {chk.detail}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Action Preview Button */}
              {rec.eligible && (
                <div style={{ marginTop: '14px', display: 'flex', justifyContent: 'flex-end' }}>
                  <button
                    className="btn btn-secondary"
                    style={{ fontSize: 'var(--font-size-xs)', padding: '6px 12px' }}
                    onClick={() => setPreviewRec(rec)}
                  >
                    💬 Preview WhatsApp Message
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* WhatsApp Preview Modal */}
      {previewRec && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            backdropFilter: 'blur(4px)',
          }}
          onClick={() => setPreviewRec(null)}
        >
          <div
            className="card"
            style={{
              width: '90%',
              maxWidth: '480px',
              backgroundColor: '#0b141a',
              border: '1px solid #202c33',
              borderRadius: '16px',
              padding: '24px',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <span style={{ fontSize: '1.25rem' }}>📱</span>
                <strong>WhatsApp Message Preview</strong>
              </div>
              <span className="simulated-label">SIMULATED ADAPTER</span>
            </div>

            <div
              style={{
                backgroundColor: '#111b21',
                borderRadius: '10px',
                padding: '16px',
                marginBottom: '16px',
                borderLeft: '4px solid #00a884',
              }}
            >
              <div
                style={{
                  fontSize: 'var(--font-size-xs)',
                  color: '#8696a0',
                  marginBottom: '8px',
                }}
              >
                To: <span className="mono">{previewRec.customer_id}</span> ({previewRec.segment_label})
              </div>
              <div
                style={{
                  fontSize: 'var(--font-size-sm)',
                  color: '#e9edef',
                  lineHeight: 1.5,
                  whiteSpace: 'pre-line',
                }}
              >
                {getTemplatePreview(previewRec)}
              </div>
              <div
                style={{
                  fontSize: '0.65rem',
                  color: '#8696a0',
                  textAlign: 'right',
                  marginTop: '8px',
                }}
              >
                12:45 PM ✓✓
              </div>
            </div>

            <div className="alert alert-warning mb-4" style={{ fontSize: 'var(--font-size-xs)' }}>
              <span>ℹ️</span>
              <div>
                <strong>Simulation Guard:</strong> Meta WhatsApp Business credentials are mock-only in
                this environment. No actual messages or egress charges will be incurred.
              </div>
            </div>

            <div className="flex justify-between">
              <button className="btn btn-secondary" onClick={() => setPreviewRec(null)}>
                Close
              </button>
              <button
                className="btn btn-success"
                onClick={() => {
                  alert(
                    `[SIMULATED DISPATCH SUCCESS]\nPayload queued for ${previewRec.customer_id} via MockWhatsAppAdapter.\nEvent logged in audit trail.`
                  );
                  setPreviewRec(null);
                }}
              >
                🚀 Simulate Send
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
