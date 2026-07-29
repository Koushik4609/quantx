import { apiClient, handleApiError } from './client';

export interface StrategyCondition {
  indicator: string;
  operator: string;
  value: number;
  timeperiod?: number;
}

export interface StrategyConditions {
  entry: StrategyCondition[];
  exit: StrategyCondition[];
}

export interface Strategy {
  id: string;
  name: string;
  symbol: string;
  timeframe: string;
  conditions: StrategyConditions;
}

export interface TradeResult {
  type: string;
  date: string;
  price: number;
  shares: number;
}

export interface BacktestResult {
  id: string;
  strategy_id: string;
  total_return: number;
  win_rate: number;
  max_drawdown: number;
  trades: TradeResult[];
}

export const getStrategies = async (userId: string): Promise<Strategy[]> => {
  try {
    const response = await apiClient.get(`/strategy/?user_id=${userId}`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const createStrategy = async (userId: string, data: Omit<Strategy, 'id'>): Promise<Strategy> => {
  try {
    const response = await apiClient.post('/strategy/', {
      user_id: userId,
      ...data
    });
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const deleteStrategy = async (id: string): Promise<void> => {
  try {
    await apiClient.delete(`/strategy/${id}`);
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const runBacktest = async (id: string): Promise<BacktestResult> => {
  try {
    const response = await apiClient.post(`/strategy/${id}/backtest`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getBacktests = async (id: string): Promise<BacktestResult[]> => {
  try {
    const response = await apiClient.get(`/strategy/${id}/backtests`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};
