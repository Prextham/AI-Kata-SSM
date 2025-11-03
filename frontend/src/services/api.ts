import axios from 'axios';
import type { AuthResponse, LoginCredentials, RegisterData, Sweet, SweetFormData, SearchParams } from '../types/index';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: async (data: RegisterData): Promise<any> => {
    const response = await api.post('/api/auth/register', data);
    return response.data;
  },

  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post<AuthResponse>('/api/auth/login', formData);
    return response.data;
  },
};

// Sweets API
export const sweetsAPI = {
  getAll: async (): Promise<Sweet[]> => {
    const response = await api.get<Sweet[]>('/api/sweets');
    return response.data;
  },

  search: async (params: SearchParams): Promise<Sweet[]> => {
    const response = await api.get<Sweet[]>('/api/sweets/search', { params });
    return response.data;
  },

  create: async (data: SweetFormData): Promise<Sweet> => {
    const response = await api.post<Sweet>('/api/sweets', data);
    return response.data;
  },

  update: async (id: number, data: Partial<SweetFormData>): Promise<Sweet> => {
    const response = await api.put<Sweet>(`/api/sweets/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/sweets/${id}`);
  },

  purchase: async (id: number, quantity: number): Promise<any> => {
    const response = await api.post(`/api/sweets/${id}/purchase`, { quantity });
    return response.data;
  },

  restock: async (id: number, quantity: number): Promise<any> => {
    const response = await api.post(`/api/sweets/${id}/restock`, { quantity });
    return response.data;
  },
};

export default api;
