import { apiClient, handleApiError } from './client';

export const buyOrder = async (portfolioId: string, symbol: string, quantity: number, price: number) => {
  try {
    const response = await apiClient.post('/trading/buy', {
      portfolio_id: portfolioId,
      symbol,
      quantity,
      price,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const sellOrder = async (portfolioId: string, symbol: string, quantity: number, price: number) => {
  try {
    const response = await apiClient.post('/trading/sell', {
      portfolio_id: portfolioId,
      symbol,
      quantity,
      price,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getPortfolio = async (portfolioId: string, currentPrices: Record<string, number> = {}) => {
  try {
    const response = await apiClient.post('/trading/portfolio', {
      portfolio_id: portfolioId,
      current_prices: currentPrices,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getTransactions = async (portfolioId: string) => {
  try {
    const response = await apiClient.get(`/trading/transactions/${portfolioId}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};
