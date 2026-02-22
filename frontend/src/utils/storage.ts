import { TOKEN_KEY, REFRESH_TOKEN_KEY } from './constants';

export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

export const setToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
};

export const getRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

export const setRefreshToken = (token: string): void => {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
};

export const removeRefreshToken = (): void => {
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

export const clearTokens = (): void => {
  removeToken();
  removeRefreshToken();
};

export const setTokens = (accessToken: string, refreshToken: string): void => {
  setToken(accessToken);
  setRefreshToken(refreshToken);
};
