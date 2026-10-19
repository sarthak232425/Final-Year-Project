/* TypeScript type definitions for all API response shapes. */

export interface ValidationIssue {
  row_number: number | null;
  field: string;
  value: string;
  reason: string;
}

export interface CleaningSummary {
  run_id: string;
  original_row_count: number;
  final_row_count: number;
  cancellation_count: number;
  dropped_missing_customer_id: number;
  dropped_missing_invoice_id: number;
  dropped_invalid_date: number;
  dropped_invalid_quantity: number;
  dropped_invalid_price: number;
  dropped_duplicates: number;
  total_dropped: number;
  issues: ValidationIssue[];
}

export interface IngestResponse {
  success: boolean;
  message: string;
  summary: CleaningSummary;
}

export interface CustomerRFM {
  customer_id: string;
  recency_days: number;
  frequency: number;
  monetary: number;
  r_score: number;
  f_score: number;
  m_score: number;
  rfm_score: number;
}

export interface RFMResult {
  run_id: string;
  reference_date: string;
  customer_count: number;
  dataset_median_recency: number;
  dataset_median_frequency: number;
  dataset_median_monetary: number;
  customers: CustomerRFM[];
}

export interface KValueMetric {
  k: number;
  silhouette: number | null;
}

export interface ClusteringMetrics {
  run_id: string;
  selected_k: number;
  silhouette_score: number | null;
  davies_bouldin_index: number | null;
  calinski_harabasz_score: number | null;
  k_evaluation: KValueMetric[];
  random_seed: number;
}

export interface AnalysisRunResponse {
  success: boolean;
  run_id: string;
  message: string;
  rfm: RFMResult;
  metrics: ClusteringMetrics;
}

export interface SegmentProfile {
  cluster_id: number;
  label: string;
  size: number;
  median_recency_days: number;
  median_frequency: number;
  median_monetary: number;
  example_customer_ids: string[];
}

export interface SegmentListResponse {
  run_id: string;
  selected_k: number;
  segments: SegmentProfile[];
}

export interface EligibilityCheck {
  check: string;
  passed: boolean;
  detail: string;
}

export interface Recommendation {
  customer_id: string;
  segment_label: string;
  campaign_type: string;
  campaign_type_display: string;
  heuristic_score: number;
  explanation: string;
  supporting_data: Record<string, unknown>;
  eligible: boolean;
  ineligibility_reason: string | null;
  eligibility_checks: EligibilityCheck[];
}

export interface RecommendationListResponse {
  run_id: string;
  total: number;
  eligible_count: number;
  ineligible_count: number;
  recommendations: Recommendation[];
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  service: string;
  version: string;
}
