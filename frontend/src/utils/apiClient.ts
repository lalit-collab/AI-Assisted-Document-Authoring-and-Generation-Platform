/**
 * API Client Configuration
 */
import axios, {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
} from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');

    if (token) {
      // Ensure headers object exists
      if (!config.headers) {
        config.headers = {};
      }
      (config.headers as any).Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error: any) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken && error.config) {
        try {
          // Optional: avoid infinite loop
          const originalRequest = error.config as InternalAxiosRequestConfig & {
            _retry?: boolean;
          };

          if (originalRequest._retry) {
            throw error;
          }
          originalRequest._retry = true;

          const response = await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            {
              refresh_token: refreshToken,
            }
          );

          const { access_token } = (response.data as any).data;
          localStorage.setItem('access_token', access_token);

          if (!originalRequest.headers) {
            originalRequest.headers = {};
          }
          (originalRequest.headers as any).Authorization = `Bearer ${access_token}`;

          return apiClient(originalRequest);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
