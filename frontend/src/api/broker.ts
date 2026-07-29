import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const getBrokerStatus = async () => {
  const token = localStorage.getItem('token');
  const response = await axios.get(`${API_URL}/broker/status`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};

export const getBrokerLoginUrl = async () => {
  const token = localStorage.getItem('token');
  const response = await axios.get(`${API_URL}/broker/upstox/login-url`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data.url;
};

export const getBrokerProfile = async () => {
  const token = localStorage.getItem('token');
  const response = await axios.get(`${API_URL}/broker/profile`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};

export const getBrokerFunds = async () => {
  const token = localStorage.getItem('token');
  const response = await axios.get(`${API_URL}/broker/funds`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};

export const getBrokerHoldings = async () => {
  const token = localStorage.getItem('token');
  const response = await axios.get(`${API_URL}/broker/holdings`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};

export const getBrokerOrders = async () => {
  const token = localStorage.getItem('token');
  const response = await axios.get(`${API_URL}/broker/orders`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};
