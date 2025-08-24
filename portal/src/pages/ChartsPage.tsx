import React from 'react';
import ChartsGallery from '../components/ChartsGallery';
import { BarChart3, TrendingUp, Filter, Search, Grid, List } from 'lucide-react';

const ChartsPage: React.FC = () => {
  return (
    <div className="charts-page">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <div className="hero-icon">
            <BarChart3 className="h-12 w-12 text-white" />
          </div>
          <h1 className="hero-title">نمودارهای تحلیلی</h1>
          <p className="hero-description">
            تحلیل جامع داده‌های تقلب در نسخه‌های پزشکی با نمودارهای تعاملی و پیشرفته
          </p>
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number">12</span>
              <span className="stat-label">نوع نمودار</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">6</span>
              <span className="stat-label">دسته‌بندی</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">24/7</span>
              <span className="stat-label">دسترسی</span>
            </div>
          </div>
        </div>
        <div className="hero-background">
          <div className="bg-gradient"></div>
          <div className="floating-shapes">
            <div className="shape shape-1"></div>
            <div className="shape shape-2"></div>
            <div className="shape shape-3"></div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content-wrapper">
        <ChartsGallery />
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <div className="quick-action-card">
          <TrendingUp className="h-6 w-6 text-primary-600" />
          <h3>آخرین روندها</h3>
          <p>مشاهده روندهای اخیر در تشخیص تقلب</p>
        </div>
        <div className="quick-action-card">
          <Filter className="h-6 w-6 text-primary-600" />
          <h3>فیلتر پیشرفته</h3>
          <p>فیلتر نمودارها بر اساس معیارهای مختلف</p>
        </div>
        <div className="quick-action-card">
          <Search className="h-6 w-6 text-primary-600" />
          <h3>جستجوی سریع</h3>
          <p>یافتن نمودار مورد نظر در کمترین زمان</p>
        </div>
      </div>
    </div>
  );
};

export default ChartsPage;
