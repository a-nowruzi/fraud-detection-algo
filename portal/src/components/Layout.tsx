import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, BarChart3, Home, Menu, Settings, User, LogOut } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    // Check if we're on mobile (client-side only)
    if (typeof window !== 'undefined') {
      return window.innerWidth > 768;
    }
    return true; // Default for SSR
  });

  const navigation = [
    { name: 'داشبورد', href: '/', icon: Home },
    { name: 'نمودارها', href: '/charts', icon: BarChart3 },
    // { name: 'آمار سیستم', href: '/stats', icon: Activity },
    { name: 'تست API', href: '/api-test', icon: Settings },
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
    // Handle window resize for sidebar state
    const handleResize = () => {
      if (window.innerWidth <= 768) {
        setSidebarOpen(false); // Hide sidebar on mobile
      } else {
        setSidebarOpen(true); // Show sidebar on desktop
      }
    };

    // Set initial state
    handleResize();

    // Add event listener
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => window.removeEventListener('resize', handleResize);
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

  // Fix dropdown transform styles
  useEffect(() => {
    const fixDropdownTransform = () => {
      const dropdownMenus = document.querySelectorAll('.dropdown-menu');
      dropdownMenus.forEach(menu => {
        if (menu instanceof HTMLElement) {
          menu.style.transform = 'none';
        }
      });
    };

    // Fix on mount
    fixDropdownTransform();

    // Fix when dropdowns are shown
    const handleDropdownShow = () => {
      setTimeout(fixDropdownTransform, 10);
    };

    document.addEventListener('show.bs.dropdown', handleDropdownShow);

    // Cleanup
    return () => {
      document.removeEventListener('show.bs.dropdown', handleDropdownShow);
    };
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
                  <span className="logo-txt">سامانه جامع تشخیص تقلب</span>
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
            <div className="dropdown d-inline-block" style={{ marginLeft: '25px' }}>
              <button
                type="button"
                className="btn header-item bg-light-subtle border-start border-end"
                id="page-header-user-dropdown"
                data-bs-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="false">
                <div className="rounded-circle header-profile-user" style={{ width: '32px', height: '32px', backgroundColor: '#5156be', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', marginLeft: '5px' }}>
                  <User className="h-4 w-4" />
                </div>
                <span className="d-none d-xl-inline-block ms-1 fw-medium">مدیر سیستم</span>
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
      <div className={`vertical-menu ${sidebarOpen ? 'show' : 'hidden'}`}>
        <div data-simplebar className="h-100">
          <div id="sidebar-menu">
            <ul className="metismenu list-unstyled" id="side-menu">
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
                <h5 className="alertcard-title font-size-16 text-black">بررسی تقلب</h5>
                <p className="font-size-13 text-black">برای بررسی نسخه جدید، بر روی دکمه زیر کلیک کنید.</p>
                <Link to="/predict" className="btn btn-primary mt-2">نسخه جدید</Link>
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
          2025 © سیستم تشخیص تقلب پزشکی
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
