import { apiClient, handleApiError } from './client';

export interface ScreenerStock {
  symbol: string;
  price: number;
  change_percent: number;
  volume: number;
  market_cap: number;
  sector: string;
}

export interface HeatmapSector {
  sector: string;
  performance: number;
  stocks: ScreenerStock[];
}

export interface FinancialStatement {
  date: string;
  total_revenue?: number;
  net_income?: number;
  operating_income?: number;
  total_assets?: number;
  total_liabilities?: number;
}

export interface CalendarEvent {
  symbol: string;
  date: string;
  type: string;
  value?: number;
}

export interface InstitutionalHolder {
  holder: string;
  shares: number;
  date_reported: string;
  percent_out: number;
}

export interface InsiderTrade {
  insider: string;
  position: string;
  date: string;
  shares: number;
  transaction_type: string;
  value: number;
}

export const getScreener = async (): Promise<ScreenerStock[]> => {
  try {
    const response = await apiClient.get('/analytics/screener');
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getHeatmap = async (): Promise<HeatmapSector[]> => {
  try {
    const response = await apiClient.get('/analytics/heatmap');
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getFinancials = async (ticker: string): Promise<FinancialStatement[]> => {
  try {
    const response = await apiClient.get(`/analytics/${ticker}/financials`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getCalendar = async (): Promise<CalendarEvent[]> => {
  try {
    const response = await apiClient.get('/analytics/calendar');
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getInstitutional = async (ticker: string): Promise<InstitutionalHolder[]> => {
  try {
    const response = await apiClient.get(`/analytics/${ticker}/institutional`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getInsider = async (ticker: string): Promise<InsiderTrade[]> => {
  try {
    const response = await apiClient.get(`/analytics/${ticker}/insider`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};
