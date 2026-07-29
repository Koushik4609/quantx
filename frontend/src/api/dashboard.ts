import { apiClient, handleApiError } from './client';

export const getPortfolioHealth = async (portfolioId: string) => {
  try {
    const response = await apiClient.get(`/ai/portfolio-health/${portfolioId}`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getDailyBrief = async () => {
  try {
    const response = await apiClient.get(`/ai/daily-brief`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getMarketMovers = async () => {
  try {
    const response = await apiClient.get(`/market/movers`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getMarketNews = async () => {
  try {
    const response = await apiClient.get(`/market/news`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getMarketSentiment = async () => {
  try {
    const response = await apiClient.get(`/market/sentiment`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getEconomicCalendar = async () => {
  try {
    const response = await apiClient.get(`/market/calendar`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getSectorHeatmap = async () => {
  try {
    const response = await apiClient.get(`/market/heatmap`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};
