import axios from 'axios';

/**
 * HTTP client configured to communicate with the FastAPI backend
 */
const apiClient = axios.create({
  // Use a relative URL so all requests go through the Next.js Route Handler
  // (app/api/v1/[...path]/route.ts), which proxies to the FastAPI backend and avoids CORS issues.
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
