import { api } from './api';
import { setTokens, clearTokens, getRefreshToken } from '@/utils/storage';
import type { 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  User 
} from '@/types';

export const authService = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    setTokens(response.access_token, response.refresh_token);
    return response;
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/register', data);
    setTokens(response.access_token, response.refresh_token);
    return response;
  },

  logout: (): void => {
    clearTokens();
  },

  refreshToken: async (): Promise<{ access_token: string }> => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    return api.post('/auth/refresh', { refresh_token: refreshToken });
  },

  getCurrentUser: async (): Promise<User> => {
    return api.get<User>('/auth/me');
  },
};
