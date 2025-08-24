import React from 'react';
import ApiTester from '../components/ApiTester';

const ApiTestPage: React.FC = () => {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">تست API</h1>
        <p className="text-gray-600">
          تست تمام endpoint های موجود در سیستم تشخیص تقلب
        </p>
      </div>
      
      <ApiTester />
    </div>
  );
};

export default ApiTestPage;
