import axios from 'axios';

/**
 * HTTP client configured to communicate with the FastAPI backend
 */
const apiClient = axios.create({
  // Use relative URL so all requests go through the Next.js proxy (next.config.ts)
  // This avoids CORS issues: /api/v1/* → http://backend:8000/api/v1/* (server-side)
  baseURL: '',
  timeout: 30000,
});

/**
 * Request interceptor - Add custom headers if needed
 */
apiClient.interceptors.request.use(
  (config) => {
    // You can add authentication tokens here if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - Handle errors globally
 */
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Centralized error handling
    if (error.response) {
      // The server responded with an error code
      console.error('Response error:', error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Request error:', error.request);
    } else {
      // Something else failed
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
