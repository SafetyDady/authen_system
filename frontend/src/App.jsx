/**
 * Main App Component - Authentication System
 */

import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import useAuthStore from './store/authStore';
import ProtectedRoute, { SuperAdminRoute, AdminRoute } from './components/ProtectedRoute';
import DashboardLayout from './components/layout/DashboardLayout';
import LoginPage from './pages/LoginPage';
import OverviewPage from './pages/dashboard/OverviewPage';
import './App.css';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Placeholder components for other pages
const AdminManagementPage = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-lg p-6 border border-gray-300 shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Admin Management</h2>
      <p className="text-gray-500">
        Manage admin users (Admin1, Admin2, Admin3). This page is only accessible by SuperAdmin.
      </p>
      <div className="mt-4 p-4 bg-gray-100 rounded-lg">
        <p className="text-sm">
          <strong>Features:</strong>
        </p>
        <ul className="text-sm text-gray-500 mt-2 space-y-1">
          <li>• Create, update, delete admin users</li>
          <li>• Assign roles (Admin1, Admin2, Admin3)</li>
          <li>• Lock/unlock admin accounts</li>
          <li>• View admin activity logs</li>
        </ul>
      </div>
    </div>
  </div>
);

const Admin1Page = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-lg p-6 border border-gray-300 shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Admin 1 - User Management</h2>
      <p className="text-gray-500">
        Manage users assigned to Admin 1. Create, update, and monitor user accounts.
      </p>
      <div className="mt-4 p-4 bg-gray-100 rounded-lg">
        <p className="text-sm">
          <strong>Permissions:</strong>
        </p>
        <ul className="text-sm text-gray-500 mt-2 space-y-1">
          <li>• Create and manage regular users</li>
          <li>• View user activity and statistics</li>
          <li>• Lock/unlock user accounts</li>
          <li>• Generate user reports</li>
        </ul>
      </div>
    </div>
  </div>
);

const Admin2Page = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-lg p-6 border border-gray-300 shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Admin 2 - User Management</h2>
      <p className="text-gray-500">
        Manage users assigned to Admin 2. Create, update, and monitor user accounts.
      </p>
      <div className="mt-4 p-4 bg-gray-100 rounded-lg">
        <p className="text-sm">
          <strong>Permissions:</strong>
        </p>
        <ul className="text-sm text-gray-500 mt-2 space-y-1">
          <li>• Create and manage regular users</li>
          <li>• View user activity and statistics</li>
          <li>• Lock/unlock user accounts</li>
          <li>• Generate user reports</li>
        </ul>
      </div>
    </div>
  </div>
);

const Admin3Page = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-lg p-6 border border-gray-300 shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Admin 3 - User Management</h2>
      <p className="text-gray-500">
        Manage users assigned to Admin 3. Create, update, and monitor user accounts.
      </p>
      <div className="mt-4 p-4 bg-gray-100 rounded-lg">
        <p className="text-sm">
          <strong>Permissions:</strong>
        </p>
        <ul className="text-sm text-gray-500 mt-2 space-y-1">
          <li>• Create and manage regular users</li>
          <li>• View user activity and statistics</li>
          <li>• Lock/unlock user accounts</li>
          <li>• Generate user reports</li>
        </ul>
      </div>
    </div>
  </div>
);

const ProfilePage = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-lg p-6 border border-gray-300 shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Profile Settings</h2>
      <p className="text-gray-500">
        Manage your profile information and account settings.
      </p>
      <div className="mt-4 p-4 bg-gray-100 rounded-lg">
        <p className="text-sm">
          <strong>Available Settings:</strong>
        </p>
        <ul className="text-sm text-gray-500 mt-2 space-y-1">
          <li>• Update personal information</li>
          <li>• Change password</li>
          <li>• Upload profile picture</li>
          <li>• Manage notification preferences</li>
        </ul>
      </div>
    </div>
  </div>
);

const UnauthorizedPage = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-100">
    <div className="text-center">
      <h1 className="text-4xl font-bold text-red-600 mb-4">403</h1>
      <h2 className="text-xl font-semibold mb-2">Access Denied</h2>
      <p className="text-gray-500 mb-4">
        You don't have permission to access this resource.
      </p>
      <button
        onClick={() => window.history.back()}
        className="text-blue-600 hover:underline"
      >
        Go Back
      </button>
    </div>
  </div>
);

const NotFoundPage = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-100">
    <div className="text-center">
      <h1 className="text-4xl font-bold text-gray-500 mb-4">404</h1>
      <h2 className="text-xl font-semibold mb-2">Page Not Found</h2>
      <p className="text-gray-500 mb-4">
        The page you're looking for doesn't exist.
      </p>
      <button
        onClick={() => window.location.href = '/dashboard/overview'}
        className="text-blue-600 hover:underline"
      >
        Go to Dashboard
      </button>
    </div>
  </div>
);

function App() {
  const { initializeAuth, isAuthenticated } = useAuthStore();

  // Initialize authentication on app start
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Routes>
            {/* Public Routes */}
            <Route 
              path="/login" 
              element={
                isAuthenticated ? (
                  <Navigate to="/dashboard/overview" replace />
                ) : (
                  <LoginPage />
                )
              } 
            />

            {/* Protected Dashboard Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              {/* Dashboard Overview - Available to all authenticated users */}
              <Route path="overview" element={<OverviewPage />} />

              {/* Admin Management - SuperAdmin only */}
              <Route
                path="admin-management"
                element={
                  <SuperAdminRoute>
                    <AdminManagementPage />
                  </SuperAdminRoute>
                }
              />

              {/* Admin Pages - Available to respective admins and superadmin */}
              <Route
                path="admin1"
                element={
                  <AdminRoute>
                    <Admin1Page />
                  </AdminRoute>
                }
              />
              <Route
                path="admin2"
                element={
                  <AdminRoute>
                    <Admin2Page />
                  </AdminRoute>
                }
              />
              <Route
                path="admin3"
                element={
                  <AdminRoute>
                    <Admin3Page />
                  </AdminRoute>
                }
              />
            </Route>

            {/* Profile Page - Available to all authenticated users */}
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />

            {/* Error Pages */}
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            <Route path="/404" element={<NotFoundPage />} />

            {/* Default Redirects */}
            <Route 
              path="/" 
              element={
                <Navigate 
                  to={isAuthenticated ? "/dashboard/overview" : "/login"} 
                  replace 
                />
              } 
            />
            <Route 
              path="/dashboard" 
              element={<Navigate to="/dashboard/overview" replace />} 
            />

            {/* Catch all - 404 */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;

