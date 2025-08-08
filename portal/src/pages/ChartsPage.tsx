import React from 'react';
import ChartsGallery from '../components/ChartsGallery';

const ChartsPage: React.FC = () => {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">نمودارهای تحلیلی</h1>
        <p className="text-gray-600">
          نمودارهای مختلف برای تحلیل داده‌های تقلب در نسخه‌های پزشکی
        </p>
      </div>
      
      <ChartsGallery />
    </div>
  );
};

export default ChartsPage;
