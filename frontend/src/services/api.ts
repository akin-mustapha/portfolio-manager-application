import axios from 'axios';
import { 
  ApiResponse, 
  ApiError,
  SessionCreate, 
  SessionResponse, 
  TokenRefresh, 
  TokenResponse, 
  Trading212APISetup, 
  Trading212APIResponse, 
  APIKeyValidation 
} from '../types/api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

console.log('API Base URL:', API_BASE_URL);

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
        const { accessToken } = JSON.parse(authData);
        if (accessToken) {
          config.headers['Authorization'] = `Bearer ${accessToken}`;
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

// Response interceptor for handling errors and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    console.error('API Error:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      method: error.config?.method,
      baseURL: error.config?.baseURL
    });
    
    const originalRequest = error.config;
    
    // Handle 401 errors with token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const authData = localStorage.getItem('trading212_auth');
      if (authData) {
        try {
          const { refreshToken } = JSON.parse(authData);
          if (refreshToken) {
            // Try to refresh the token
            const refreshResponse = await apiClient.post('/auth/refresh', {
              refresh_token: refreshToken
            });
            
            if (refreshResponse.data.data) {
              const { access_token, expires_in } = refreshResponse.data.data;
              
              // Update stored auth data
              const updatedAuth = {
                ...JSON.parse(authData),
                accessToken: access_token,
                tokenExpiresAt: new Date(Date.now() + expires_in * 1000)
              };
              localStorage.setItem('trading212_auth', JSON.stringify(updatedAuth));
              
              // Retry original request with new token
              originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
              return apiClient(originalRequest);
            }
          }
        } catch (refreshError) {
          console.warn('Token refresh failed:', refreshError);
        }
      }
      
      // If refresh fails, clear auth and emit error
      localStorage.removeItem('trading212_auth');
      window.dispatchEvent(new CustomEvent('auth-error'));
    }

    const apiError: ApiError = {
      message: error.response?.data?.detail || error.response?.data?.message || error.message || 'An unexpected error occurred',
      code: error.response?.data?.code || error.code,
      status: error.response?.status,
      details: error.response?.data?.details,
    };

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
  // Session Management
  createSession: async (sessionData: SessionCreate): Promise<ApiResponse<SessionResponse>> => {
    return api.post('/auth/session', sessionData);
  },

  refreshToken: async (tokenData: TokenRefresh): Promise<ApiResponse<TokenResponse>> => {
    return api.post('/auth/refresh', tokenData);
  },

  deleteSession: async (): Promise<ApiResponse<{ message: string }>> => {
    return api.delete('/auth/session');
  },

  // Trading 212 API Management
  setupTrading212API: async (apiSetup: Trading212APISetup): Promise<ApiResponse<Trading212APIResponse>> => {
    return api.post('/auth/trading212/setup', apiSetup);
  },

  validateTrading212API: async (apiSetup: Trading212APISetup): Promise<ApiResponse<APIKeyValidation>> => {
    return api.post('/auth/trading212/validate', apiSetup);
  },

  removeTrading212API: async (): Promise<ApiResponse<{ message: string }>> => {
    return api.delete('/auth/trading212/setup');
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