import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Home, User, FileText, Briefcase, MessageSquare, LogOut, Mail, TrendingUp, Play, Sparkles, Settings, Menu, X } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };

  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/profile', icon: User, label: 'Profile' },
    { path: '/jobs', icon: Briefcase, label: 'Jobs' },
    { path: '/resumes', icon: FileText, label: 'Resumes' },
    { path: '/resume-intelligence', icon: TrendingUp, label: 'Intelligence' },
    { path: '/cover-letters', icon: Mail, label: 'Cover Letters' },
    { path: '/interview-prep', icon: MessageSquare, label: 'Interview Prep' },
    { path: '/practice-sessions', icon: Play, label: 'Practice' },
    { path: '/live-interview/sessions', icon: Sparkles, label: 'Live Assistant' },
    { path: '/admin/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <>
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-40 bg-white shadow-md">
        <div className="flex items-center justify-between px-4 h-16">
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-md text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 transition-colors"
            aria-label="Toggle menu"
          >
            <Menu size={24} />
          </button>
          
          <Link to="/dashboard" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">R</span>
            </div>
            <span className="text-lg font-bold text-secondary-900">ResuMatch AI</span>
          </Link>

          <div className="w-10"></div>
        </div>
      </div>

      {/* Overlay for mobile */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={closeSidebar}
        ></div>
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0`}
        data-testid="navbar"
      >
        <div className="flex flex-col h-full">
          {/* Logo Section */}
          <div className="flex items-center justify-between px-6 h-16 border-b border-secondary-200">
            <Link to="/dashboard" className="flex items-center space-x-2" onClick={closeSidebar}>
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">R</span>
              </div>
              <span className="text-lg font-bold text-secondary-900">ResuMatch AI</span>
            </Link>
            
            <button
              onClick={closeSidebar}
              className="lg:hidden p-1 rounded-md text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100"
              aria-label="Close menu"
            >
              <X size={20} />
            </button>
          </div>

          {/* Navigation Items */}
          <nav className="flex-1 px-3 py-6 overflow-y-auto">
            <div className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={closeSidebar}
                    data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
                    className={`flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-primary-50 text-primary-700 border-l-4 border-primary-600'
                        : 'text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900 border-l-4 border-transparent'
                    }`}
                  >
                    <Icon size={20} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </nav>

          {/* User Section */}
          <div className="border-t border-secondary-200 px-3 py-4">
            <div className="px-4 py-3 bg-secondary-50 rounded-lg mb-2">
              <div className="text-sm font-medium text-secondary-900 truncate">
                {user?.full_name}
              </div>
              <div className="text-xs text-secondary-600 truncate mt-1">
                {user?.email}
              </div>
              <div className="mt-2">
                <span className="inline-block px-2 py-1 text-xs bg-primary-100 text-primary-800 rounded-full">
                  {user?.subscription_tier || 'free'}
                </span>
              </div>
            </div>
            
            <button
              onClick={handleLogout}
              data-testid="logout-button"
              className="flex items-center space-x-3 px-4 py-3 w-full rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut size={20} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Navbar;
