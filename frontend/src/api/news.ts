import { apiClient, handleApiError } from './client';

export interface NewsArticle {
  id: string;
  title: string;
  source: string;
  url: string;
  published_at: string;
  related_tickers: string[];
  summary: string;
}

export interface Bookmark {
  id: string;
  user_id: string;
  article_url: string;
  article_title: string;
  source?: string;
  published_at?: string;
  created_at: string;
}

export const getMarketNews = async (): Promise<NewsArticle[]> => {
  try {
    const response = await apiClient.get('/news/market');
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getCompanyNews = async (ticker: string): Promise<NewsArticle[]> => {
  try {
    const response = await apiClient.get(`/news/company/${ticker}`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const summarizeArticle = async (url: string): Promise<{summary: string}> => {
  try {
    const response = await apiClient.post('/news/summarize', { url });
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const getBookmarks = async (userId: string): Promise<Bookmark[]> => {
  try {
    const response = await apiClient.get(`/news/bookmarks/${userId}`);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const addBookmark = async (bookmark: Partial<Bookmark>): Promise<Bookmark> => {
  try {
    const response = await apiClient.post('/news/bookmarks', bookmark);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};

export const removeBookmark = async (bookmarkId: string): Promise<void> => {
  try {
    await apiClient.delete(`/news/bookmarks/${bookmarkId}`);
  } catch (error) {
    throw new Error(handleApiError(error));
  }
};
