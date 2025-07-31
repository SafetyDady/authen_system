/**
 * Protected Route component for authentication and authorization
 */

import { Navigate, useLocation } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const ProtectedRoute = ({ 
  children, 
  requireAuth = true, 
  requiredRoles = [], 
  redirectTo = '/login' 
}) => {
  const { isAuthenticated, user, hasAnyRole } = useAuthStore();
  const location = useLocation();

  // If authentication is required but user is not authenticated
  if (requireAuth && !isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // If specific roles are required
  if (requiredRoles.length > 0 && !hasAnyRole(requiredRoles)) {
    // Redirect based on user role
    if (user?.role === 'superadmin') {
      return <Navigate to="/dashboard/overview" replace />;
    } else if (['admin1', 'admin2', 'admin3'].includes(user?.role)) {
      return <Navigate to="/dashboard/overview" replace />;
    } else {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return children;
};

// Higher-order component for role-based protection
export const withRoleProtection = (Component, requiredRoles = []) => {
  return (props) => (
    <ProtectedRoute requiredRoles={requiredRoles}>
      <Component {...props} />
    </ProtectedRoute>
  );
};

// Specific role protection components
export const SuperAdminRoute = ({ children }) => (
  <ProtectedRoute requiredRoles={['superadmin']}>
    {children}
  </ProtectedRoute>
);

export const AdminRoute = ({ children }) => (
  <ProtectedRoute requiredRoles={['superadmin', 'admin1', 'admin2', 'admin3']}>
    {children}
  </ProtectedRoute>
);

export const UserRoute = ({ children }) => (
  <ProtectedRoute requiredRoles={['superadmin', 'admin1', 'admin2', 'admin3', 'user']}>
    {children}
  </ProtectedRoute>
);

export default ProtectedRoute;

