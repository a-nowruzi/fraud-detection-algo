import React from 'react';
import StatsDashboard from '../components/StatsDashboard';

const StatsPage: React.FC = () => {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">آمار سیستم</h1>
        <p className="text-gray-600">
          آمار کلی و عملکرد سیستم تشخیص تقلب پزشکی
        </p>
      </div>
      
      <StatsDashboard />
    </div>
  );
};

export default StatsPage;
