import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, BarChart3, Activity, Home, Menu, Settings } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { name: 'داشبورد', href: '/', icon: Home },
    { name: 'تشخیص تقلب', href: '/predict', icon: Shield },
    { name: 'نمودارها', href: '/charts', icon: BarChart3 },
    { name: 'آمار سیستم', href: '/stats', icon: Activity },
  ];

  return (
    <div id="layout-wrapper" dir="rtl">
      {/* Header */}
      <header id="page-topbar">
        <div className="navbar-header">
          <div className="d-flex">
            {/* LOGO */}
            <div className="navbar-brand-box">
              <Link to="/" className="logo logo-dark">
                <span className="logo-sm">
                  <Shield className="h-6 w-6" />
                </span>
                <span className="logo-lg">
                  <Shield className="h-6 w-6" />
                  <span className="logo-txt">تشخیص تقلب</span>
                </span>
              </Link>
            </div>

            <button
              type="button"
              className="btn btn-sm px-3 font-size-16 header-item"
              id="vertical-menu-btn"
              onClick={() => setSidebarOpen(!sidebarOpen)}>
              <Menu className="h-4 w-4" />
            </button>

          </div>
        </div>
      </header>

      {/* Right Sidebar */}
      <div className={`vertical-menu ${sidebarOpen ? 'show' : ''}`}>
        <div className="h-100">
          <div id="sidebar-menu">
            <ul className="metismenu list-unstyled" id="side-menu">
              <li className="menu-title">منو</li>

              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <li key={item.name}>
                    <Link
                      to={item.href}
                      className={isActive ? 'active' : ''}
                    >
                      <item.icon className="h-4 w-4 ml-2" />
                      <span>{item.name}</span>
                    </Link>
                  </li>
                );
              })}

              <li className="menu-title mt-2">سیستم</li>

              <li>
                <a href="#settings">
                  <Settings className="h-4 w-4 ml-2" />
                  <span>تنظیمات</span>
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="page-content">
          {children}
        </div>

        {/* Footer */}
        <footer className="footer">
          <div className="container-fluid">
            <div className="row">
              <div className="col-sm-6">
                2025 © سیستم تشخیص تقلب پزشکی
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Layout;
