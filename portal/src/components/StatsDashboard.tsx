import React, { useState, useEffect } from 'react';
import { apiService, type SystemStats } from '../services/api';
import { Activity, AlertTriangle, CheckCircle, TrendingUp, Database } from 'lucide-react';

const StatsDashboard: React.FC = () => {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await apiService.getStats();
      setStats(data);
    } catch (err) {
      setError('خطا در دریافت آمار سیستم');
      console.error('Stats error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-8">
        <div className="text-red-600 mb-4">{error}</div>
        <button onClick={fetchStats} className="btn-primary">
          تلاش مجدد
        </button>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const statCards = [
    {
      title: 'کل نسخه‌ها',
      value: stats.total_prescriptions.toLocaleString('fa-IR'),
      icon: Database,
      color: 'bg-blue-500',
      textColor: 'text-blue-600',
    },
    {
      title: 'نسخه‌های سالم',
      value: stats.normal_prescriptions.toLocaleString('fa-IR'),
      icon: CheckCircle,
      color: 'bg-green-500',
      textColor: 'text-green-600',
    },
    {
      title: 'نسخه‌های مشکوک',
      value: stats.fraud_prescriptions.toLocaleString('fa-IR'),
      icon: AlertTriangle,
      color: 'bg-red-500',
      textColor: 'text-red-600',
    },
    {
      title: 'درصد تقلب',
      value: `${stats.fraud_percentage.toFixed(2)}%`,
      icon: TrendingUp,
      color: 'bg-yellow-500',
      textColor: 'text-yellow-600',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">آمار کلی سیستم</h2>
        <button onClick={fetchStats} className="btn-secondary">
          <Activity className="ml-2 h-4 w-4" />
          به‌روزرسانی
        </button>
      </div>

      {/* کارت‌های آمار */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => (
          <div key={index} className="card">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${card.color} text-white`}>
                <card.icon className="h-6 w-6" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-600">{card.title}</p>
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* جزئیات بیشتر */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">اطلاعات مدل</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">نوع مدل:</span>
              <span className="font-medium">Isolation Forest</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">میزان آلودگی:</span>
              <span className="font-medium">{(stats.model_contamination * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">تعداد ویژگی‌ها:</span>
              <span className="font-medium">{stats.features_count}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">نسبت‌ها</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">نسخه‌های سالم</span>
                <span className="text-sm font-medium text-gray-700">
                  {((stats.normal_prescriptions / stats.total_prescriptions) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{ width: `${(stats.normal_prescriptions / stats.total_prescriptions) * 100}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">نسخه‌های مشکوک</span>
                <span className="text-sm font-medium text-gray-700">
                  {((stats.fraud_prescriptions / stats.total_prescriptions) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-600 h-2 rounded-full"
                  style={{ width: `${(stats.fraud_prescriptions / stats.total_prescriptions) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* خلاصه عملکرد */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">خلاصه عملکرد سیستم</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <div className="text-lg font-semibold text-green-700">
              {((stats.normal_prescriptions / stats.total_prescriptions) * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-green-600">نرخ تشخیص صحیح</div>
          </div>
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <Database className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <div className="text-lg font-semibold text-blue-700">
              {stats.total_prescriptions.toLocaleString('fa-IR')}
            </div>
            <div className="text-sm text-blue-600">کل رکوردهای پردازش شده</div>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <AlertTriangle className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
            <div className="text-lg font-semibold text-yellow-700">
              {stats.fraud_prescriptions.toLocaleString('fa-IR')}
            </div>
            <div className="text-sm text-yellow-600">نسخه‌های مشکوک شناسایی شده</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsDashboard;
