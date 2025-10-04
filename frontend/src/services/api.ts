import axios from 'axios';
import { ApiResponse, ApiError } from '../types/api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens
apiClient.interceptors.request.use(
  (config) => {
    const authData = localStorage.getItem('trading212_auth');
    if (authData) {
      try {
        const { apiKey } = JSON.parse(authData);
        if (apiKey) {
          config.headers['X-API-Key'] = apiKey;
        }
      } catch (error) {
        console.warn('Failed to parse auth data:', error);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const apiError: ApiError = {
      message: error.response?.data?.message || error.message || 'An unexpected error occurred',
      code: error.response?.data?.code || error.code,
      status: error.response?.status,
      details: error.response?.data?.details,
    };

    // Handle specific error cases
    if (error.response?.status === 401) {
      // Clear auth data on unauthorized
      localStorage.removeItem('trading212_auth');
      window.dispatchEvent(new CustomEvent('auth-error'));
    }

    return Promise.reject(apiError);
  }
);

// Generic API functions
export const api = {
  get: <T>(url: string): Promise<ApiResponse<T>> =>
    apiClient.get(url).then((response) => response.data),
  
  post: <T>(url: string, data?: any): Promise<ApiResponse<T>> =>
    apiClient.post(url, data).then((response) => response.data),
  
  put: <T>(url: string, data?: any): Promise<ApiResponse<T>> =>
    apiClient.put(url, data).then((response) => response.data),
  
  delete: <T>(url: string): Promise<ApiResponse<T>> =>
    apiClient.delete(url).then((response) => response.data),
};

// Specific API service functions
export const apiService = {
  // Authentication
  validateApiKey: async (apiKey: string): Promise<ApiResponse<{ valid: boolean }>> => {
    return api.post('/auth/validate', { api_key: apiKey });
  },

  // Portfolio data
  getPortfolio: async (): Promise<ApiResponse<any>> => {
    return api.get('/portfolio');
  },

  getPies: async (): Promise<ApiResponse<any[]>> => {
    return api.get('/pies');
  },

  // Health check
  healthCheck: async (): Promise<ApiResponse<{ status: string }>> => {
    return api.get('/health');
  },
};

// Health check function
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get('/health');
    return response.status === 200;
  } catch (error) {
    return false;
  }
};