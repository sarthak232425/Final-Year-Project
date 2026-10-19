/**
 * API client — thin wrapper around fetch.
 * All calls go through Vite's proxy to avoid CORS issues in development.
 */

const BASE_URL = '/api/v1';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Accept': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const err = await response.json();
      detail = err.detail || detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail);
  }

  return response.json();
}

export const api = {
  health: () =>
    fetch('/health').then(r => r.json()),

  uploadCSV: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<import('../types').IngestResponse>('/ingest/upload', {
      method: 'POST',
      body: formData,
    });
  },

  getIngestionStatus: () =>
    request('/ingest/status'),

  runAnalysis: () =>
    request<import('../types').AnalysisRunResponse>('/analysis/run', {
      method: 'POST',
    }),

  getRFM: (page = 1, pageSize = 50) =>
    request(`/analysis/rfm?page=${page}&page_size=${pageSize}`),

  getMetrics: () =>
    request<import('../types').ClusteringMetrics>('/analysis/metrics'),

  getSegments: () =>
    request<import('../types').SegmentListResponse>('/segments'),

  getSegmentCustomers: (clusterId: number) =>
    request(`/segments/${clusterId}/customers`),

  getRecommendations: (params?: {
    eligible_only?: boolean;
    segment_label?: string;
    page?: number;
    page_size?: number;
  }) => {
    const q = new URLSearchParams();
    if (params?.eligible_only) q.set('eligible_only', 'true');
    if (params?.segment_label) q.set('segment_label', params.segment_label);
    if (params?.page) q.set('page', String(params.page));
    if (params?.page_size) q.set('page_size', String(params.page_size));
    return request<import('../types').RecommendationListResponse>(
      `/recommendations?${q.toString()}`
    );
  },

  previewCampaign: (body: {
    campaign_type: string;
    segment_label?: string;
    frequency_cap?: number;
  }) =>
    request('/campaigns/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
};
