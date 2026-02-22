export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const TOKEN_KEY = 'pdf_reports_access_token';
export const REFRESH_TOKEN_KEY = 'pdf_reports_refresh_token';

export const REPORTS_PER_PAGE = 20;

export const STATUS_LABELS: Record<string, string> = {
  pending: 'Pending',
  processing: 'Processing',
  completed: 'Completed',
  failed: 'Failed',
};

export const DATA_SOURCE_LABELS: Record<string, string> = {
  sql: 'SQL Database',
  api: 'REST API',
  csv: 'CSV File',
};

export const POLL_INTERVAL = 3000; // 3 seconds

export const DEBOUNCE_DELAY = 300; // 300ms

export const CRON_PRESETS = [
  { label: 'Every hour', value: '0 * * * *' },
  { label: 'Every day at midnight', value: '0 0 * * *' },
  { label: 'Every day at 9 AM', value: '0 9 * * *' },
  { label: 'Every Monday at 9 AM', value: '0 9 * * 1' },
  { label: 'Every month on the 1st', value: '0 0 1 * *' },
];
