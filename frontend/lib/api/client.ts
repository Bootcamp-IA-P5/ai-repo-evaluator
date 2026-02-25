import axios from 'axios';

/**
 * Cliente HTTP configurado para comunicarse con el backend FastAPI
 */
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Interceptor de peticiones - Añade headers personalizados si es necesario
 */
apiClient.interceptors.request.use(
  (config) => {
    // Aquí puedes añadir tokens de autenticación si los usas
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
 * Interceptor de respuestas - Maneja errores globalmente
 */
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Manejo centralizado de errores
    if (error.response) {
      // El servidor respondió con un código de error
      console.error('Error de respuesta:', error.response.data);
    } else if (error.request) {
      // La petición fue hecha pero no hubo respuesta
      console.error('Error de petición:', error.request);
    } else {
      // Algo más falló
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
