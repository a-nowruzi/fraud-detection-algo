import React from 'react';
import PredictionForm from '../components/PredictionForm';

const PredictPage: React.FC = () => {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">تشخیص تقلب در نسخه پزشکی</h1>
        <p className="text-gray-600">
          اطلاعات نسخه پزشکی را وارد کنید تا سیستم احتمال تقلب را تشخیص دهد
        </p>
      </div>
      
      <PredictionForm />
    </div>
  );
};

export default PredictPage;
