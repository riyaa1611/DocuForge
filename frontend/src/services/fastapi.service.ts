/**
 * FastAPI Backend Service
 * 
 * This service handles calls to your FastAPI backend for PDF generation.
 * Configure VITE_API_URL in your .env file to point to your backend.
 * 
 * Local development: VITE_API_URL=http://localhost:8000/api/v1
 * Production: VITE_API_URL=https://your-backend.com/api/v1
 */

import { API_BASE_URL } from '@/utils/constants';
import { getToken } from '@/utils/storage';
import type { DataSource, ReportCreateRequest } from '@/types';

interface FastAPIError extends Error {
  status?: number;
  detail?: string;
}

interface GenerateReportRequest {
  template_id: string;
  data_source: DataSource;
  params?: Record<string, unknown>;
}

interface GenerateReportResponse {
  job_id: string;
  report_id: string;
  status: string;
  message?: string;
}

interface ReportStatusResponse {
  report_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  file_path?: string;
  error_message?: string;
  progress?: number;
}

interface HealthCheckResponse {
  status: string;
  version?: string;
}

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const error: FastAPIError = new Error('API request failed');
    error.status = response.status;
    try {
      const data = await response.json();
      error.detail = data.detail || data.message || 'Unknown error';
      error.message = error.detail;
    } catch {
      error.detail = `HTTP ${response.status}`;
    }
    throw error;
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
};

const getHeaders = (): HeadersInit => {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

export const fastapiService = {
  /**
   * Check if the FastAPI backend is reachable
   */
  healthCheck: async (): Promise<HealthCheckResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
        headers: getHeaders(),
      });
      return handleResponse<HealthCheckResponse>(response);
    } catch (error) {
      console.warn('FastAPI backend not reachable:', error);
      throw error;
    }
  },

  /**
   * Generate a PDF report via FastAPI backend
   */
  generateReport: async (request: GenerateReportRequest): Promise<GenerateReportResponse> => {
    const response = await fetch(`${API_BASE_URL}/reports/generate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(request),
    });
    return handleResponse<GenerateReportResponse>(response);
  },

  /**
   * Check the status of a report generation job
   */
  getReportStatus: async (reportId: string): Promise<ReportStatusResponse> => {
    const response = await fetch(`${API_BASE_URL}/reports/${reportId}/status`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse<ReportStatusResponse>(response);
  },

  /**
   * Download a generated report
   */
  downloadReport: async (reportId: string, filename?: string): Promise<void> => {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/reports/${reportId}/download`, {
      method: 'GET',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      throw new Error('Download failed');
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || `report-${reportId}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  },

  /**
   * Sync a report creation with FastAPI (hybrid mode)
   * Creates in Supabase first, then triggers FastAPI for PDF generation
   */
  triggerGeneration: async (reportId: string, request: ReportCreateRequest): Promise<GenerateReportResponse> => {
    const response = await fetch(`${API_BASE_URL}/reports/${reportId}/generate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        template_id: request.template_id,
        data_source: request.data_source,
        params: request.params,
      }),
    });
    return handleResponse<GenerateReportResponse>(response);
  },
};

/**
 * Check if FastAPI backend is configured and reachable
 */
export const isBackendConfigured = (): boolean => {
  return API_BASE_URL !== 'http://localhost:8000/api/v1' || 
         import.meta.env.VITE_API_URL !== undefined;
};

/**
 * Get the configured API URL for debugging
 */
export const getApiUrl = (): string => API_BASE_URL;
