import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, BarChart3, Activity, Home, Menu, Settings, User, LogOut } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navigation = [
    { name: 'داشبورد', href: '/', icon: Home },
    { name: 'تشخیص تقلب', href: '/predict', icon: Shield },
    { name: 'نمودارها', href: '/charts', icon: BarChart3 },
    { name: 'آمار سیستم', href: '/stats', icon: Activity },
  ];

  useEffect(() => {
    // Initialize Minia theme functionality
    if (typeof window !== 'undefined') {
      // Add any Minia-specific initialization here
      document.body.setAttribute('data-layout', 'vertical');
      document.body.setAttribute('data-sidebar', 'light');
      document.body.setAttribute('data-topbar', 'light');
    }
  }, []);

  useEffect(() => {
    // Hide preloader when component mounts
    const hidePreloader = () => {
      const preloader = document.getElementById('preloader');
      if (preloader) {
        preloader.style.opacity = '0';
        setTimeout(() => {
          preloader.style.display = 'none';
        }, 300);
      }
    };

    // Hide preloader after a short delay to ensure smooth transition
    const timer = setTimeout(hidePreloader, 500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div id="layout-wrapper" dir="rtl">
      {/* Header */}
      <header id="page-topbar">
        <div className="navbar-header">
          <div className="d-flex">
            {/* LOGO */}
            <div className="navbar-brand-box">

              <Link to="/" className="logo logo-light">
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

          <div className="d-flex">

            {/* User Profile */}
            <div className="dropdown d-inline-block">
              <button
                type="button"
                className="btn header-item bg-light-subtle border-start border-end"
                id="page-header-user-dropdown"
                data-bs-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="false">
                <div className="rounded-circle header-profile-user" style={{ width: '32px', height: '32px', backgroundColor: '#5156be', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
                  <User className="h-4 w-4" />
                </div>
                <span className="d-none d-xl-inline-block ms-1 fw-medium">کاربر</span>
              </button>
              <div className="dropdown-menu dropdown-menu-end">
                <Link to="/profile" className="dropdown-item">
                  <span className="font-size-16 align-middle me-1"><Settings className="h-4 w-4" /></span> پروفایل
                </Link>
                <div className="dropdown-divider"></div>
                <Link to="/logout" className="dropdown-item">
                  <span className="font-size-16 align-middle me-1"><LogOut className="h-4 w-4" /></span> خروج
                </Link>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Right Sidebar */}
      <div className={`vertical-menu ${sidebarOpen ? '' : 'hidden'}`}>
        <div data-simplebar className="h-100">
          <div id="sidebar-menu">
            <ul className="metismenu list-unstyled" id="side-menu">
              <li className="menu-title" data-key="t-menu">منو</li>

              {
                navigation.map((item) => {
                  const isActive = location.pathname === item.href;
                  return (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={isActive ? 'active' : ''}>
                        <item.icon className="h-4 w-4" style={{ marginLeft: '7px' }} />
                        <span>{item.name}</span>
                      </Link>
                    </li>
                  );
                })}
            </ul>

            <div className="card sidebar-alert border-0 text-center mx-4 mb-0 mt-5">
              <div className="card-body">
                  <h5 className="alertcard-title font-size-16">بررسی تقلب</h5>
                  <p className="font-size-13">برای بررسی نسخه جدید، بر روی دکمه زیر کلیک کنید.</p>
                  <Link to="/upload" className="btn btn-primary mt-2">نسخه جدید</Link>
                </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className={`main-content ${sidebarOpen ? '' : 'sidebar-hidden'}`}>
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
              <div className="col-sm-6">
                <div className="text-sm-end d-none d-sm-block">
                  طراحی و توسعه توسط <a href="#!" className="text-decoration-underline">تیم توسعه</a>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default Layout;
