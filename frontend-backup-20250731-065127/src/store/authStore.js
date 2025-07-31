/**
 * Authentication store using Zustand
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI, apiUtils } from '../lib/api';

const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      // Actions
      login: async (credentials) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authAPI.login(credentials);
          const authData = response.data;
          
          // Store auth data
          apiUtils.setAuth(authData);
          
          set({
            user: authData.user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          
          return { success: true, data: authData };
        } catch (error) {
          const errorInfo = apiUtils.handleError(error);
          set({
            isLoading: false,
            error: errorInfo.message,
            isAuthenticated: false,
            user: null,
          });
          
          return { success: false, error: errorInfo };
        }
      },

      logout: async (logoutAllDevices = false) => {
        set({ isLoading: true });
        
        try {
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            await authAPI.logout({
              refresh_token: refreshToken,
              logout_all_devices: logoutAllDevices,
            });
          }
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          // Clear auth data regardless of API call result
          apiUtils.clearAuth();
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      refreshToken: async () => {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          get().logout();
          return { success: false, error: 'No refresh token' };
        }

        try {
          const response = await authAPI.refresh(refreshToken);
          const { access_token } = response.data;
          
          localStorage.setItem('access_token', access_token);
          
          return { success: true, data: { access_token } };
        } catch (error) {
          const errorInfo = apiUtils.handleError(error);
          get().logout();
          return { success: false, error: errorInfo };
        }
      },

      updateProfile: async (profileData) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authAPI.getMe();
          const updatedUser = response.data;
          
          // Update user in localStorage
          localStorage.setItem('user', JSON.stringify(updatedUser));
          
          set({
            user: updatedUser,
            isLoading: false,
            error: null,
          });
          
          return { success: true, data: updatedUser };
        } catch (error) {
          const errorInfo = apiUtils.handleError(error);
          set({
            isLoading: false,
            error: errorInfo.message,
          });
          
          return { success: false, error: errorInfo };
        }
      },

      verifyToken: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
          set({ isAuthenticated: false, user: null });
          return { success: false, error: 'No token' };
        }

        try {
          const response = await authAPI.verifyToken();
          const userData = response.data.user;
          
          set({
            user: userData,
            isAuthenticated: true,
            error: null,
          });
          
          return { success: true, data: userData };
        } catch (error) {
          const errorInfo = apiUtils.handleError(error);
          apiUtils.clearAuth();
          set({
            user: null,
            isAuthenticated: false,
            error: errorInfo.message,
          });
          
          return { success: false, error: errorInfo };
        }
      },

      initializeAuth: () => {
        const token = localStorage.getItem('access_token');
        const userStr = localStorage.getItem('user');
        
        if (token && userStr) {
          try {
            const user = JSON.parse(userStr);
            set({
              user,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
            
            // Verify token in background
            get().verifyToken();
          } catch (error) {
            console.error('Error parsing user data:', error);
            apiUtils.clearAuth();
            set({
              user: null,
              isAuthenticated: false,
              isLoading: false,
              error: null,
            });
          }
        } else {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      clearError: () => {
        set({ error: null });
      },

      // Computed properties
      hasRole: (role) => {
        const { user } = get();
        return user?.role === role;
      },

      hasAnyRole: (roles) => {
        const { user } = get();
        return roles.includes(user?.role);
      },

      isSuperAdmin: () => {
        return get().hasRole('superadmin');
      },

      isAdmin: () => {
        return get().hasAnyRole(['superadmin', 'admin1', 'admin2', 'admin3']);
      },

      canManageUsers: () => {
        return get().isAdmin();
      },

      canManageAdmins: () => {
        return get().isSuperAdmin();
      },

      getUserDisplayName: () => {
        const { user } = get();
        if (!user) return '';
        return user.full_name || `${user.first_name} ${user.last_name}` || user.email;
      },

      getUserRole: () => {
        const { user } = get();
        return user?.role || '';
      },

      getUserRoleLabel: () => {
        const role = get().getUserRole();
        const roleLabels = {
          superadmin: 'Super Admin',
          admin1: 'Admin 1',
          admin2: 'Admin 2',
          admin3: 'Admin 3',
          user: 'User',
        };
        return roleLabels[role] || role;
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;

