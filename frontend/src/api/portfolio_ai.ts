import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const getPortfolioIntelligence = async (userId: string) => {
  const token = localStorage.getItem('token');
  const response = await axios.get(`${API_URL}/portfolio/intelligence/?user_id=${userId}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};
