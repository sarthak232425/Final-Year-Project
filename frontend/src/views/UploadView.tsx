import React, { useState } from 'react';
import { api } from '../api/client';
import { CleaningSummary } from '../types';

interface UploadViewProps {
  onAnalysisComplete: () => void;
  cleaningSummary: CleaningSummary | null;
  setCleaningSummary: (summary: CleaningSummary | null) => void;
}

export const UploadView: React.FC<UploadViewProps> = ({
  onAnalysisComplete,
  cleaningSummary,
  setCleaningSummary,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleFileUpload = async (file: File) => {
    if (!file.name.endsWith('.csv')) {
      setError('Please upload a valid .csv file');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const response = await api.uploadCSV(file);
      setCleaningSummary(response.summary);
      setSuccessMessage(
        `File "${file.name}" uploaded successfully! Ingested ${response.summary.final_row_count} valid records.`
      );
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleLoadSample = async () => {
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      // Create a blob representing the example dataset
      const sampleCsv = `invoice_id,customer_id,invoice_date,quantity,unit_price,consent_given,suppressed,messages_last_30_days
INV001,CUST001,2024-01-15,3,12.50,true,false,0
INV001,CUST001,2024-01-15,2,8.00,true,false,0
INV002,CUST001,2024-02-20,5,15.00,true,false,0
INV003,CUST002,2024-03-01,1,45.00,true,false,1
INV004,CUST002,2024-03-10,2,22.50,true,false,1
INV005,CUST003,2023-11-05,10,5.00,false,false,0
INV006,CUST003,2023-12-01,4,12.00,false,false,0
INV007,CUST004,2024-03-14,8,30.00,true,false,4
INV008,CUST005,2023-08-10,1,100.00,true,false,0
INV009,CUST006,2024-03-12,3,15.00,true,true,0
INV010,CUST007,2024-02-28,2,60.00,true,false,0
INV011,CUST008,2023-10-15,1,250.00,true,false,0
INV012,CUST009,2024-03-15,6,18.00,true,false,1
INV013,CUST010,2023-09-20,2,35.00,true,false,0
INV014,CUST011,2024-01-25,12,8.50,true,false,2
INV015,CUST012,2024-03-11,4,55.00,true,false,0
INV016,CUST013,2023-12-22,1,15.00,true,false,0
INV017,CUST014,2024-03-05,7,40.00,true,false,1
INV018,CUST015,2023-07-04,3,25.00,true,false,0
CINV01,CUST001,2024-02-21,-1,15.00,true,false,0
BAD001,,2024-01-01,1,10.00,true,false,0
BAD002,CUST999,invalid-date,1,10.00,true,false,0
BAD003,CUST999,2024-01-01,-5,10.00,true,false,0
BAD004,CUST999,2024-01-01,1,-10.00,true,false,0`;

      const file = new File([sampleCsv], 'example_transactions.csv', { type: 'text/csv' });
      const response = await api.uploadCSV(file);
      setCleaningSummary(response.summary);
      setSuccessMessage('Loaded built-in example dataset (15 customers, edge cases & intentional invalid rows).');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load sample dataset');
    } finally {
      setLoading(false);
    }
  };

  const handleRunAnalysis = async () => {
    setAnalyzing(true);
    setError(null);
    try {
      await api.runAnalysis();
      onAnalysisComplete();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Analysis failed to run');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="page-body">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h2>Data Ingestion & Validation</h2>
          <p>Upload raw retail transaction logs or import the standard benchmark dataset</p>
        </div>
        <button
          className="btn btn-secondary"
          onClick={handleLoadSample}
          disabled={loading || analyzing}
        >
          📂 Load Example Dataset
        </button>
      </div>

      {error && (
        <div className="alert alert-error mb-6">
          <span>⚠️</span>
          <div>
            <strong>Error:</strong> {error}
          </div>
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success mb-6">
          <span>✓</span>
          <div>{successMessage}</div>
        </div>
      )}

      <div
        className={`upload-zone mb-8 ${isDragging ? 'drag-over' : ''}`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById('csv-file-input')?.click()}
      >
        <input
          type="file"
          id="csv-file-input"
          accept=".csv"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        <span className="upload-icon">📊</span>
        <h3>Drag & Drop Transaction CSV Here</h3>
        <p>Supports Online Retail dataset format (InvoiceNo, CustomerID, InvoiceDate, Quantity, UnitPrice)</p>
        <p style={{ marginTop: '8px' }}>
          <span className="badge badge-primary">Automatic Data Cleaning & Aliasing</span>
        </p>
      </div>

      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <span>Parsing and validating data records...</span>
        </div>
      )}

      {cleaningSummary && (
        <div className="card mb-8">
          <div className="card-header">
            <div>
              <div className="card-title">Data Cleaning & Validation Summary</div>
              <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                Run ID: <span className="mono">{cleaningSummary.run_id}</span>
              </p>
            </div>
            <button
              className="btn btn-primary"
              onClick={handleRunAnalysis}
              disabled={analyzing}
            >
              {analyzing ? '⏳ Running ML Pipeline...' : '⚡ Run RFM & Clustering'}
            </button>
          </div>

          <div className="metric-grid">
            <div className="metric-card">
              <div className="metric-label">Original Rows</div>
              <div className="metric-value">{cleaningSummary.original_row_count}</div>
              <div className="metric-sub">Total records received</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Valid Ingested</div>
              <div className="metric-value success">{cleaningSummary.final_row_count}</div>
              <div className="metric-sub">Clean rows stored</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Cancellations Detected</div>
              <div className="metric-value warning">{cleaningSummary.cancellation_count}</div>
              <div className="metric-sub">Prefix 'C' isolated</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Invalid Rows Dropped</div>
              <div className="metric-value danger">{cleaningSummary.total_dropped}</div>
              <div className="metric-sub">Removed by quality rules</div>
            </div>
          </div>

          <div className="grid-2 mb-6">
            <div className="card" style={{ background: 'var(--color-surface)' }}>
              <div className="card-title mb-4">Rejection Breakdown</div>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <li className="flex justify-between">
                  <span>Missing Customer ID:</span>
                  <strong className="mono">{cleaningSummary.dropped_missing_customer_id}</strong>
                </li>
                <li className="flex justify-between">
                  <span>Missing Invoice ID:</span>
                  <strong className="mono">{cleaningSummary.dropped_missing_invoice_id}</strong>
                </li>
                <li className="flex justify-between">
                  <span>Invalid Date Format:</span>
                  <strong className="mono">{cleaningSummary.dropped_invalid_date}</strong>
                </li>
                <li className="flex justify-between">
                  <span>Non-positive Quantity:</span>
                  <strong className="mono">{cleaningSummary.dropped_invalid_quantity}</strong>
                </li>
                <li className="flex justify-between">
                  <span>Non-positive Price:</span>
                  <strong className="mono">{cleaningSummary.dropped_invalid_price}</strong>
                </li>
                <li className="flex justify-between">
                  <span>Duplicate Records:</span>
                  <strong className="mono">{cleaningSummary.dropped_duplicates}</strong>
                </li>
              </ul>
            </div>

            <div className="card" style={{ background: 'var(--color-surface)' }}>
              <div className="card-title mb-4">Pipeline Quality Gate</div>
              <p style={{ fontSize: 'var(--font-size-sm)', marginBottom: '12px' }}>
                Integrity checks prevent corrupted transaction records from skewing customer RFM
                percentiles and clustering centroids.
              </p>
              <div className="progress-bar mb-2">
                <div
                  className="progress-fill"
                  style={{
                    width: `${
                      cleaningSummary.original_row_count > 0
                        ? (cleaningSummary.final_row_count / cleaningSummary.original_row_count) * 100
                        : 0
                    }%`,
                  }}
                ></div>
              </div>
              <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                Clean Retention Rate:{' '}
                {cleaningSummary.original_row_count > 0
                  ? (
                      (cleaningSummary.final_row_count / cleaningSummary.original_row_count) *
                      100
                    ).toFixed(1)
                  : 0}
                %
              </span>
            </div>
          </div>

          {cleaningSummary.issues.length > 0 && (
            <div>
              <div className="card-title mb-2">Detected Issue Log (Sample)</div>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Row #</th>
                      <th>Field</th>
                      <th>Value</th>
                      <th>Validation Rule Violated</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cleaningSummary.issues.slice(0, 10).map((issue, idx) => (
                      <tr key={idx}>
                        <td className="mono">{issue.row_number ?? 'N/A'}</td>
                        <td>
                          <span className="badge badge-warning">{issue.field}</span>
                        </td>
                        <td className="mono">{issue.value || '""'}</td>
                        <td>{issue.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
