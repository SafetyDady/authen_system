/**
 * API client for Authentication System
 */

import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(
            `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/auth/refresh`,
            { refresh_token: refreshToken }
          );

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  logout: (data) => api.post('/auth/logout', data),
  refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
  getMe: () => api.get('/auth/me'),
  requestPasswordReset: (email) => api.post('/auth/password-reset', { email }),
  confirmPasswordReset: (data) => api.post('/auth/password-reset/confirm', data),
  verifyToken: () => api.post('/auth/verify-token'),
  getSessions: () => api.get('/auth/sessions'),
  revokeSession: (sessionId) => api.delete(`/auth/sessions/${sessionId}`),
};

// Users API
export const usersAPI = {
  getUsers: (params) => api.get('/users', { params }),
  getUser: (userId) => api.get(`/users/${userId}`),
  createUser: (userData) => api.post('/users', userData),
  updateUser: (userId, userData) => api.put(`/users/${userId}`, userData),
  deleteUser: (userId) => api.delete(`/users/${userId}`),
  lockUser: (userId) => api.post(`/users/${userId}/lock`),
  unlockUser: (userId) => api.post(`/users/${userId}/unlock`),
  getMyProfile: () => api.get('/users/me'),
  updateMyProfile: (profileData) => api.put('/users/me', profileData),
  changePassword: (passwordData) => api.post('/users/me/change-password', passwordData),
  getUserStats: () => api.get('/users/stats'),
  getUserAuditLogs: (userId, params) => api.get(`/users/${userId}/audit-logs`, { params }),
};

// Admin API
export const adminAPI = {
  getAdmins: () => api.get('/admin/admins'),
  getAdmin: (adminId) => api.get(`/admin/admins/${adminId}`),
  createAdmin: (adminData) => api.post('/admin/admins', adminData),
  updateAdmin: (adminId, adminData) => api.put(`/admin/admins/${adminId}`, adminData),
  deleteAdmin: (adminId) => api.delete(`/admin/admins/${adminId}`),
  lockAdmin: (adminId) => api.post(`/admin/admins/${adminId}/lock`),
  unlockAdmin: (adminId) => api.post(`/admin/admins/${adminId}/unlock`),
  getSystemStats: () => api.get('/admin/system/stats'),
  getSystemAuditLogs: (params) => api.get('/admin/audit-logs', { params }),
  getAvailableRoles: () => api.get('/admin/roles'),
};

// Generic API functions
export const apiUtils = {
  handleError: (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      return {
        message,
        status: error.response.status,
        errors: error.response.data?.errors || [],
      };
    } else if (error.request) {
      // Request was made but no response received
      return {
        message: 'Network error. Please check your connection.',
        status: 0,
        errors: [],
      };
    } else {
      // Something else happened
      return {
        message: error.message || 'An unexpected error occurred',
        status: 0,
        errors: [],
      };
    }
  },

  isAuthenticated: () => {
    const token = localStorage.getItem('access_token');
    return !!token;
  },

  getUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  setAuth: (authData) => {
    localStorage.setItem('access_token', authData.access_token);
    localStorage.setItem('refresh_token', authData.refresh_token);
    localStorage.setItem('user', JSON.stringify(authData.user));
  },

  clearAuth: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  hasRole: (role) => {
    const user = apiUtils.getUser();
    return user?.role === role;
  },

  hasAnyRole: (roles) => {
    const user = apiUtils.getUser();
    return roles.includes(user?.role);
  },

  isSuperAdmin: () => {
    return apiUtils.hasRole('superadmin');
  },

  isAdmin: () => {
    return apiUtils.hasAnyRole(['superadmin', 'admin1', 'admin2', 'admin3']);
  },

  canManageUsers: () => {
    return apiUtils.isAdmin();
  },

  canManageAdmins: () => {
    return apiUtils.isSuperAdmin();
  },
};

export default api;

