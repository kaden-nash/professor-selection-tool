import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Example request function
export const getItems = async () => {
  const response = await api.get('/items');
  return response.data;
};

export default api;