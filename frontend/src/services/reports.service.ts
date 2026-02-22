import { api } from './api';
import type { 
  Report, 
  ReportCreateRequest, 
  ReportListResponse,
  ReportStatus
} from '@/types';

export interface ReportFilters {
  status?: ReportStatus | 'all';
  template_id?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  limit?: number;
}

export const reportsService = {
  /**
   * Get a paginated list of reports with optional filters
   */
  getReports: async (filters?: ReportFilters): Promise<ReportListResponse> => {
    const params: Record<string, string | number> = {};
    
    if (filters) {
      if (filters.status && filters.status !== 'all') params.status = filters.status;
      if (filters.template_id) params.template_id = filters.template_id;
      if (filters.date_from) params.date_from = filters.date_from;
      if (filters.date_to) params.date_to = filters.date_to;
      if (filters.page) params.page = filters.page;
if (filters.limit) params.limit = filters.limit;
    }

    const response = await api.get<ReportListResponse>('/reports', { params });
    return response;
  },

  /**
   * Get a specific report by ID
   */
  getReport: async (id: string): Promise<Report> => {
    const response = await api.get<Report>(`/reports/${id}`);
    return response;
  },

  /**
   * Generate a new report
   */
  generateReport: async (request: ReportCreateRequest): Promise<{ job_id: string; status: string; message?: string }> => {
    const response = await api.post<{ job_id: string; status: string; message?: string }>('/reports/generate', request);
    return response;
  },

  /**
   * Check the status of a report
   */
  getReportStatus: async (id: string): Promise<Report> => {
    const response = await api.get<Report>(`/reports/${id}/status`);
    return response;
  },

  /**
   * Download a report PDF
   */
  downloadReport: async (id: string, filename?: string): Promise<void> => {
    await api.downloadFile(`/reports/${id}/download`, filename || `report-${id}.pdf`);
  },

  /**
   * Delete a report
   */
  deleteReport: async (id: string): Promise<void> => {
    await api.delete(`/reports/${id}`);
  },
};
