import React, { useState } from 'react';
import { apiService } from '../services/api';
import { Wifi, WifiOff, CheckCircle, XCircle, Loader2 } from 'lucide-react';

const ApiTester: React.FC = () => {
  const [healthStatus, setHealthStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [healthData, setHealthData] = useState<any>(null);
  const [statsStatus, setStatsStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [statsData, setStatsData] = useState<any>(null);

  const testHealth = async () => {
    setHealthStatus('loading');
    try {
      const data = await apiService.healthCheck();
      setHealthData(data);
      setHealthStatus('success');
    } catch (error) {
      console.error('Health check error:', error);
      setHealthStatus('error');
    }
  };

  const testStats = async () => {
    setStatsStatus('loading');
    try {
      const data = await apiService.getStats();
      setStatsData(data);
      setStatsStatus('success');
    } catch (error) {
      console.error('Stats error:', error);
      setStatsStatus('error');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'loading':
        return <Loader2 className="h-5 w-5 animate-spin text-blue-500" />;
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Wifi className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'loading':
        return 'در حال بررسی...';
      case 'success':
        return 'متصل';
      case 'error':
        return 'خطا در اتصال';
      default:
        return 'بررسی نشده';
    }
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">تست اتصال به API</h3>
      
      <div className="space-y-4">
        {/* Health Check */}
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div className="flex items-center space-x-3 space-x-reverse">
            {getStatusIcon(healthStatus)}
            <div>
              <h4 className="font-medium text-gray-900">بررسی سلامت سیستم</h4>
              <p className="text-sm text-gray-600">{getStatusText(healthStatus)}</p>
            </div>
          </div>
          <button
            onClick={testHealth}
            disabled={healthStatus === 'loading'}
            className="btn-secondary disabled:opacity-50"
          >
            تست
          </button>
        </div>

        {/* Stats Test */}
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div className="flex items-center space-x-3 space-x-reverse">
            {getStatusIcon(statsStatus)}
            <div>
              <h4 className="font-medium text-gray-900">دریافت آمار سیستم</h4>
              <p className="text-sm text-gray-600">{getStatusText(statsStatus)}</p>
            </div>
          </div>
          <button
            onClick={testStats}
            disabled={statsStatus === 'loading'}
            className="btn-secondary disabled:opacity-50"
          >
            تست
          </button>
        </div>

        {/* Results */}
        {(healthStatus === 'success' || statsStatus === 'success') && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-3">نتایج تست:</h4>
            
            {healthStatus === 'success' && healthData && (
              <div className="mb-4">
                <h5 className="font-medium text-gray-700 mb-2">وضعیت سلامت:</h5>
                <div className="text-sm text-gray-600 space-y-1">
                  <div>وضعیت: {healthData.status}</div>
                  <div>مدل بارگذاری شده: {healthData.model_loaded ? 'بله' : 'خیر'}</div>
                  <div>داده بارگذاری شده: {healthData.data_loaded ? 'بله' : 'خیر'}</div>
                  <div>زمان: {new Date(healthData.timestamp).toLocaleString('fa-IR')}</div>
                </div>
              </div>
            )}

            {statsStatus === 'success' && statsData && (
              <div>
                <h5 className="font-medium text-gray-700 mb-2">آمار سیستم:</h5>
                <div className="text-sm text-gray-600 space-y-1">
                  <div>کل نسخه‌ها: {statsData.total_prescriptions.toLocaleString('fa-IR')}</div>
                  <div>نسخه‌های مشکوک: {statsData.fraud_prescriptions.toLocaleString('fa-IR')}</div>
                  <div>درصد تقلب: {statsData.fraud_percentage.toFixed(2)}%</div>
                  <div>تعداد ویژگی‌ها: {statsData.features_count}</div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Error Messages */}
        {(healthStatus === 'error' || statsStatus === 'error') && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <WifiOff className="h-5 w-5 text-red-500 ml-2" />
              <div>
                <h4 className="font-medium text-red-700">خطا در اتصال</h4>
                <p className="text-sm text-red-600">
                  مطمئن شوید که backend روی پورت 5000 اجرا می‌شود و CORS فعال است.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ApiTester;
