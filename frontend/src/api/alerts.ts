import axios from 'axios';

const API_URL = 'http://localhost:8000';

export interface Alert {
  id?: string;
  symbol: string;
  alert_type: string;
  condition: string;
  value: number;
  status?: string;
  created_at?: string;
  triggered_at?: string;
}

export const getAlerts = async (): Promise<Alert[]> => {
  const token = localStorage.getItem('token');
  const response = await axios.get(`${API_URL}/alerts/`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};

export const createAlert = async (alert: Alert): Promise<Alert> => {
  const token = localStorage.getItem('token');
  const response = await axios.post(`${API_URL}/alerts/`, alert, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};

export const deleteAlert = async (id: string): Promise<void> => {
  const token = localStorage.getItem('token');
  await axios.delete(`${API_URL}/alerts/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};
