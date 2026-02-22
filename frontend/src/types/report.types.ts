export type ReportStatus = 'pending' | 'processing' | 'completed' | 'failed';

export type DataSourceType = 'sql' | 'api' | 'csv';

export interface DataSourceConfig {
  // SQL config
  connection_string?: string;
  query?: string;
  // API config
  url?: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  body?: string;
  // CSV config
  file_path?: string;
  file_name?: string;
  content?: string;
}

export interface DataSource {
  type: DataSourceType;
  config: DataSourceConfig;
}

export interface Report {
  id: string;
  user_id: string;
  template_id: string;
  template_name?: string;
  status: ReportStatus;
  file_path: string | null;
  file_size: number | null;
  params: Record<string, unknown>;
  data_source: DataSource;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface ReportCreateRequest {
  template_id: string;
  data_source: DataSource;
  params?: Record<string, unknown>;
}

export interface ReportGenerateResponse {
  job_id: string;
  report_id: string;
}

export interface ReportsListResponse {
  items: Report[];
  total: number;
  page: number;
  limit: number;
}

export interface ReportsFilters {
  status?: ReportStatus | 'all';
  template_id?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
  page?: number;
  limit?: number;
}
