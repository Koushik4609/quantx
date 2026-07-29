import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000'; // FastAPI backend

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

import { auth } from '../firebase';

apiClient.interceptors.request.use(async (config) => {
  // Try to get fresh Firebase token if user exists
  if (auth.currentUser) {
    try {
      const token = await auth.currentUser.getIdToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (e) {
      console.error("Error getting Firebase token", e);
    }
  } else {
    // Fallback to local storage (e.g. for mock tokens)
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Common error handler
export const handleApiError = (error: any) => {
  if (error.response) {
    throw new Error(error.response.data.detail || error.response.data.message || 'Server error');
  } else if (error.request) {
    throw new Error('Network error - please check your connection');
  }
  throw error;
};
