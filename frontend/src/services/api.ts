import { getToken, clearTokens } from '@/utils/storage';
import { API_BASE_URL } from '@/utils/constants';

interface RequestConfig extends RequestInit {
  params?: Record<string, string | number | undefined>;
}

interface ApiError extends Error {
  status?: number;
  data?: unknown;
}

const buildUrl = (endpoint: string, params?: Record<string, string | number | undefined>): string => {
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        url.searchParams.append(key, String(value));
      }
    });
  }
  return url.toString();
};

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (response.status === 401) {
    clearTokens();
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error: ApiError = new Error('API request failed');
    error.status = response.status;
    try {
      error.data = await response.json();
    } catch {
      error.data = null;
    }
    throw error;
  }

  // Handle empty responses (like DELETE)
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
};

export const api = {
  get: async <T>(endpoint: string, config?: RequestConfig): Promise<T> => {
    const token = getToken();
    const url = buildUrl(endpoint, config?.params);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...config?.headers,
      },
      ...config,
    });

    return handleResponse<T>(response);
  },

  post: async <T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> => {
    const token = getToken();
    const url = buildUrl(endpoint, config?.params);

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...config?.headers,
      },
      body: data ? JSON.stringify(data) : undefined,
      ...config,
    });

    return handleResponse<T>(response);
  },

  put: async <T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> => {
    const token = getToken();
    const url = buildUrl(endpoint, config?.params);

    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...config?.headers,
      },
      body: data ? JSON.stringify(data) : undefined,
      ...config,
    });

    return handleResponse<T>(response);
  },

  delete: async <T>(endpoint: string, config?: RequestConfig): Promise<T> => {
    const token = getToken();
    const url = buildUrl(endpoint, config?.params);

    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...config?.headers,
      },
      ...config,
    });

    return handleResponse<T>(response);
  },

  // Special method for file downloads
  downloadFile: async (endpoint: string, filename: string): Promise<void> => {
    const token = getToken();
    const url = buildUrl(endpoint);

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      throw new Error('Download failed');
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },
};
