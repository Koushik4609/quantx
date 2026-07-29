import { apiClient, handleApiError } from './client';

export const searchSymbol = async (query: string) => {
  try {
    const response = await apiClient.get(`/market/search?query=${query}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getQuote = async (symbol: string) => {
  try {
    const response = await apiClient.get(`/market/quote?symbol=${symbol}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getProfile = async (symbol: string) => {
  try {
    const response = await apiClient.get(`/market/profile?symbol=${symbol}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getMarketStatus = async () => {
  try {
    const response = await apiClient.get('/market/status');
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};
