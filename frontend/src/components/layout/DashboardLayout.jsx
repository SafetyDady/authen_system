/**
 * Dashboard Layout - Multi-Section Enterprise Design
 */

import { useState, useEffect } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Menu, 
  X, 
  Search, 
  Bell, 
  Settings, 
  User, 
  LogOut,
  ChevronDown,
  Home,
  Users,
  Shield,
  UserCheck,
  UserX,
  Activity
} from 'lucide-react';
import useAuthStore from '../../store/authStore';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger 
} from '../ui/dropdown-menu';
import { Badge } from '../ui/badge';
import '../App.css';

const DashboardLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout, getUserDisplayName, getUserRoleLabel, isSuperAdmin, isAdmin } = useAuthStore();

  // Get current section from URL
  const getCurrentSection = () => {
    const path = location.pathname;
    if (path.includes('/admin-management')) return 'admin-management';
    if (path.includes('/admin1')) return 'admin1';
    if (path.includes('/admin2')) return 'admin2';
    if (path.includes('/admin3')) return 'admin3';
    return 'overview';
  };

  const currentSection = getCurrentSection();

  // Navigation items based on user role
  const getNavigationItems = () => {
    const baseItems = [
      {
        id: 'overview',
        label: 'Overview',
        icon: Home,
        path: '/dashboard/overview',
        description: 'Dashboard overview'
      }
    ];

    if (isSuperAdmin()) {
      return [
        ...baseItems,
        {
          id: 'admin-management',
          label: 'Admin Management',
          icon: Shield,
          path: '/dashboard/admin-management',
          description: 'Manage admin users'
        },
        {
          id: 'admin1',
          label: 'Admin 1 Users',
          icon: UserCheck,
          path: '/dashboard/admin1',
          description: 'Users managed by Admin 1'
        },
        {
          id: 'admin2',
          label: 'Admin 2 Users',
          icon: UserCheck,
          path: '/dashboard/admin2',
          description: 'Users managed by Admin 2'
        },
        {
          id: 'admin3',
          label: 'Admin 3 Users',
          icon: UserCheck,
          path: '/dashboard/admin3',
          description: 'Users managed by Admin 3'
        }
      ];
    } else if (isAdmin()) {
      const adminRole = user?.role;
      return [
        ...baseItems,
        {
          id: adminRole,
          label: `${adminRole.charAt(0).toUpperCase() + adminRole.slice(1)} Users`,
          icon: Users,
          path: `/dashboard/${adminRole}`,
          description: 'Manage your users'
        }
      ];
    }

    return baseItems;
  };

  const navigationItems = getNavigationItems();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleNavigation = (path) => {
    navigate(path);
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Get page title based on current section
  const getPageTitle = () => {
    const titles = {
      'overview': 'Dashboard Overview',
      'admin-management': 'Admin Management',
      'admin1': 'Admin 1 - User Management',
      'admin2': 'Admin 2 - User Management',
      'admin3': 'Admin 3 - User Management'
    };
    return titles[currentSection] || 'Dashboard';
  };

  // Get breadcrumb items
  const getBreadcrumbs = () => {
    const breadcrumbs = [
      { label: 'Dashboard', path: '/dashboard/overview' }
    ];

    if (currentSection !== 'overview') {
      const item = navigationItems.find(item => item.id === currentSection);
      if (item) {
        breadcrumbs.push({ label: item.label, path: item.path });
      }
    }

    return breadcrumbs;
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="auth-header fixed top-0 left-0 right-0 z-50 h-16 border-b border-white/10">
        <div className="flex items-center justify-between h-full px-4">
          {/* Left side */}
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleSidebar}
              className="text-white hover:bg-white/10"
            >
              <Menu className="w-5 h-5" />
            </Button>

            {/* Breadcrumbs */}
            <nav className="hidden md:flex items-center gap-2 text-white/80 text-sm">
              {getBreadcrumbs().map((crumb, index) => (
                <div key={crumb.path} className="flex items-center gap-2">
                  {index > 0 && <span>/</span>}
                  <button
                    onClick={() => navigate(crumb.path)}
                    className="hover:text-white transition-colors"
                  >
                    {crumb.label}
                  </button>
                </div>
              ))}
            </nav>
          </div>

          {/* Center - Search */}
          <div className="flex-1 max-w-md mx-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/60" />
              <Input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/60 focus:border-white/40 focus:ring-white/20"
              />
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            {/* Notifications */}
            <Button
              variant="ghost"
              size="sm"
              className="text-white hover:bg-white/10 relative"
            >
              <Bell className="w-5 h-5" />
              <Badge className="absolute -top-1 -right-1 w-5 h-5 p-0 bg-red-500 text-white text-xs">
                3
              </Badge>
            </Button>

            {/* Settings */}
            <Button
              variant="ghost"
              size="sm"
              className="text-white hover:bg-white/10"
            >
              <Settings className="w-5 h-5" />
            </Button>

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="flex items-center gap-2 text-white hover:bg-white/10 px-3"
                >
                  <Avatar className="w-8 h-8">
                    <AvatarImage src={user?.avatar_url} />
                    <AvatarFallback className="bg-white/20 text-white text-sm">
                      {getUserDisplayName().charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="hidden md:block text-left">
                    <div className="text-sm font-medium">{getUserDisplayName()}</div>
                    <div className="text-xs text-white/70">{getUserRoleLabel()}</div>
                  </div>
                  <ChevronDown className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>My Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => navigate('/profile')}>
                  <User className="mr-2 h-4 w-4" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/settings')}>
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
import '../../App.css';
// ...existing code...
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="auth-sidebar fixed left-0 top-16 bottom-0 w-70 z-40 border-r border-white/10"
          >
            <div className="p-4">
              {/* Logo */}
              <div className="flex items-center gap-3 mb-8">
                <div className="auth-shimmer flex items-center justify-center w-10 h-10 bg-white/20 rounded-lg">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-white font-semibold">Auth System</h2>
                  <p className="text-white/70 text-xs">Enterprise Dashboard</p>
                </div>
              </div>

              {/* Navigation */}
              <nav className="space-y-2">
                {navigationItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = currentSection === item.id;
                  
                  return (
                    <motion.button
                      key={item.id}
                      onClick={() => handleNavigation(item.path)}
                      className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg text-left transition-all duration-200 ${
                        isActive
                          ? 'bg-white/20 text-white shadow-lg'
                          : 'text-white/80 hover:bg-white/10 hover:text-white'
                      }`}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Icon className="w-5 h-5 flex-shrink-0" />
                      <div className="flex-1">
                        <div className="font-medium">{item.label}</div>
                        <div className="text-xs text-white/60">{item.description}</div>
                      </div>
                      {isActive && (
                        <motion.div
                          layoutId="activeIndicator"
                          className="w-2 h-2 bg-white rounded-full"
                        />
                      )}
                    </motion.button>
                  );
                })}
              </nav>

              {/* System Status */}
              <div className="mt-8 p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center gap-2 text-white/90 text-sm mb-2">
                  <Activity className="w-4 h-4" />
                  <span className="font-medium">System Status</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-white/70 text-xs">All systems operational</span>
                </div>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main
        className={`transition-all duration-300 pt-16 ${
          sidebarOpen ? 'ml-70' : 'ml-0'
        }`}
      >
        <div className="p-6">
          {/* Page Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-foreground mb-2">
              {getPageTitle()}
            </h1>
            <p className="text-muted-foreground">
              Welcome back, {getUserDisplayName()}
            </p>
          </div>

          {/* Page Content */}
          <Outlet />
        </div>
      </main>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default DashboardLayout;

