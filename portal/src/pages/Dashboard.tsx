import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BarChart3, Activity, Users, AlertTriangle, Cpu, Database } from 'lucide-react';
import { apiService, type SystemStats, type ModelInfo } from '../services/api';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, modelData] = await Promise.all([
        apiService.getStats(),
        apiService.getModelInfo()
      ]);
      setStats(statsData);
      setModelInfo(modelData);
    } catch (err) {
      setError('خطا در دریافت اطلاعات داشبورد');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">در حال بارگذاری...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-5">
        <div className="alert alert-danger mb-4" role="alert">
          <i className="mdi mdi-alert-circle me-2"></i>
          {error}
        </div>
        <button onClick={fetchDashboardData} className="btn btn-primary">
          <i className="mdi mdi-refresh me-2"></i>
          تلاش مجدد
        </button>
      </div>
    );
  }

  return (
    <>
      <div className="row">
        <div className="col-xl-4 col-md-6">
          {/* card */}
          <div className="card card-h-100">
            {/* card body */}
            <div className="card-body">
              <div className="row align-items-center">
                <div className="col-6">
                  <span className="text-muted mb-3 lh-1 d-block text-truncate">کل نسخه‌ها</span>
                  <h4 className="mb-3">
                    <span className="counter-value" data-target={stats?.total_prescriptions || 0}>
                      {stats?.total_prescriptions.toLocaleString('fa-IR') || '0'}
                    </span>
                  </h4>
                </div>
                <div className="col-6">
                  <div className="text-center">
                    <Users className="h-8 w-8 text-primary" />
                  </div>
                </div>
              </div>
              <div className="text-nowrap">
                <span className="badge bg-success-subtle text-success">
                  {stats ? `${((stats.normal_prescriptions / stats.total_prescriptions) * 100).toFixed(1)}%` : '0%'}
                </span>
                <span className="ms-1 text-muted font-size-13">نسخه‌های سالم</span>
              </div>
            </div>
          </div>
        </div>

        <div className="col-xl-4 col-md-6">
          {/* card */}
          <div className="card card-h-100">
            {/* card body */}
            <div className="card-body">
              <div className="row align-items-center">
                <div className="col-6">
                  <span className="text-muted mb-3 lh-1 d-block text-truncate">نسخه‌های مشکوک</span>
                  <h4 className="mb-3">
                    <span className="counter-value" data-target={stats?.fraud_prescriptions || 0}>
                      {stats?.fraud_prescriptions.toLocaleString('fa-IR') || '0'}
                    </span>
                  </h4>
                </div>
                <div className="col-6">
                  <div className="text-center">
                    <AlertTriangle className="h-8 w-8 text-warning" />
                  </div>
                </div>
              </div>
              <div className="text-nowrap">
                <span className="badge bg-danger-subtle text-danger">
                  {stats ? `${stats.fraud_percentage.toFixed(2)}%` : '0%'}
                </span>
                <span className="ms-1 text-muted font-size-13">نرخ تقلب</span>
              </div>
            </div>
          </div>
        </div>

        <div className="col-xl-4 col-md-6">
          {/* card */}
          <div className="card card-h-100">
            {/* card body */}
            <div className="card-body">
              <div className="row align-items-center">
                <div className="col-6">
                  <span className="text-muted mb-3 lh-1 d-block text-truncate">نمونه‌های آموزشی</span>
                  <h4 className="mb-3">
                    <span className="counter-value" data-target={modelInfo?.training_samples || 0}>
                      {modelInfo?.training_samples.toLocaleString('fa-IR') || '0'}
                    </span>
                  </h4>
                </div>
                <div className="col-6">
                  <div className="text-center">
                    <Database className="h-8 w-8 text-success" />
                  </div>
                </div>
              </div>
              <div className="text-nowrap">
                <span className="badge bg-success-subtle text-success">
                  {modelInfo?.feature_count || 0}
                </span>
                <span className="ms-1 text-muted font-size-13">ویژگی‌ها</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-xl-8">
          {/* card */}
          <div className="card">
            {/* card body */}
            <div className="card-body">
              <div className="d-flex flex-wrap align-items-center mb-4">
                <h5 className="card-title me-2">آمار کلی سیستم</h5>
                <div className="ms-auto">
                  <div>
                    <button type="button" className="btn btn-soft-primary btn-sm">
                      همه
                    </button>
                    <button type="button" className="btn btn-soft-secondary btn-sm">
                      1M
                    </button>
                    <button type="button" className="btn btn-soft-secondary btn-sm">
                      6M
                    </button>
                    <button type="button" className="btn btn-soft-secondary btn-sm">
                      1Y
                    </button>
                  </div>
                </div>
              </div>

              <div className="row align-items-center">
                <div className="col-xl-8">
                  <div className="text-center p-4">
                    <div className="chart-placeholder" style={{ height: '300px', backgroundColor: '#f8f9fa', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '8px' }}>
                      <div className="text-center">
                        <BarChart3 className="h-16 w-16 text-muted mb-3" />
                        <h5>آمار تشخیص تقلب</h5>
                        <p className="text-muted">این نمودار آمار تشخیص تقلب را نمایش می‌دهد</p>
                        <Link to="/charts" className="btn btn-primary mt-3">
                          مشاهده نمودارها
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-xl-4">
                  <div className="p-4">
                    <div className="mt-0">
                      <div className="d-flex align-items-center">
                        <div className="avatar-sm m-auto">
                          <span className="avatar-title rounded-circle bg-light-subtle text-dark font-size-16">
                            1
                          </span>
                        </div>
                        <div className="flex-grow-1 ms-3">
                          <span className="font-size-16">نسخه‌های سالم</span>
                        </div>
                        <div className="flex-shrink-0">
                          <span className="badge rounded-pill bg-success-subtle text-success font-size-12 fw-medium">
                            {stats ? `${((stats.normal_prescriptions / stats.total_prescriptions) * 100).toFixed(1)}%` : '0%'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-3">
                      <div className="d-flex align-items-center">
                        <div className="avatar-sm m-auto">
                          <span className="avatar-title rounded-circle bg-light-subtle text-dark font-size-16">
                            2
                          </span>
                        </div>
                        <div className="flex-grow-1 ms-3">
                          <span className="font-size-16">نسخه‌های مشکوک</span>
                        </div>
                        <div className="flex-shrink-0">
                          <span className="badge rounded-pill bg-danger-subtle text-danger font-size-12 fw-medium">
                            {stats ? `${stats.fraud_percentage.toFixed(2)}%` : '0%'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-3">
                      <div className="d-flex align-items-center">
                        <div className="avatar-sm m-auto">
                          <span className="avatar-title rounded-circle bg-light-subtle text-dark font-size-16">
                            3
                          </span>
                        </div>
                        <div className="flex-grow-1 ms-3">
                          <span className="font-size-16">نرخ آلودگی مدل</span>
                        </div>
                        <div className="flex-shrink-0">
                          <span className="badge rounded-pill bg-warning-subtle text-warning font-size-12 fw-medium">
                            {stats ? `${(stats.model_contamination * 100).toFixed(2)}%` : '0%'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 pt-2">
                      <Link to="/charts" className="btn btn-primary w-100">
                        مشاهده همه نمودارها <i className="mdi mdi-arrow-right ms-1"></i>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="col-xl-4">
          <div className="card">
            <div className="card-header align-items-center d-flex">
              <h4 className="card-title mb-0 flex-grow-1">وضعیت سیستم</h4>
            </div>

            <div className="card-body px-0">
              <div className="px-3" data-simplebar style={{ maxHeight: '352px' }}>
                <ul className="list-unstyled activity-wid mb-0">
                  <li className="activity-list activity-border">
                    <div className="activity-icon avatar-md">
                      <span className={`avatar-title ${modelInfo?.status === 'ready' ? 'bg-success-subtle text-success' : 'bg-warning-subtle text-warning'} rounded-circle`}>
                        <Cpu className="font-size-24" />
                      </span>
                    </div>
                    <div className="timeline-list-item">
                      <div className="d-flex">
                        <div className="flex-grow-1 overflow-hidden me-4">
                          <h5 className="font-size-14 mb-1">وضعیت مدل</h5>
                          <p className="text-truncate text-muted font-size-13">
                            {modelInfo?.status === 'ready' ? 'مدل آماده برای پیش‌بینی' : 'مدل در حال بارگذاری'}
                          </p>
                        </div>
                        <div className="flex-shrink-0 text-end me-3">
                          <h6 className="mb-1">{modelInfo?.model_type || 'نامشخص'}</h6>
                          <div className="font-size-13">
                            {modelInfo?.status === 'ready' ? 'آماده' : 'در حال بارگذاری'}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>

                  <li className="activity-list activity-border">
                    <div className="activity-icon avatar-md">
                      <span className="avatar-title bg-primary-subtle text-primary rounded-circle">
                        <Database className="font-size-24" />
                      </span>
                    </div>
                    <div className="timeline-list-item">
                      <div className="d-flex">
                        <div className="flex-grow-1 overflow-hidden me-4">
                          <h5 className="font-size-14 mb-1">داده‌های سیستم</h5>
                          <p className="text-truncate text-muted font-size-13">
                            {stats?.total_prescriptions.toLocaleString('fa-IR') || '0'} نسخه پردازش شده
                          </p>
                        </div>
                        <div className="flex-shrink-0 text-end me-3">
                          <h6 className="mb-1">{stats?.features_count || 0}</h6>
                          <div className="font-size-13">ویژگی</div>
                        </div>
                      </div>
                    </div>
                  </li>

                  <li className="activity-list">
                    <div className="activity-icon avatar-md">
                      <span className="avatar-title bg-info-subtle text-info rounded-circle">
                        <Activity className="font-size-24" />
                      </span>
                    </div>
                    <div className="timeline-list-item">
                      <div className="d-flex">
                        <div className="flex-grow-1 overflow-hidden me-4">
                          <h5 className="font-size-14 mb-1">آمار تشخیص</h5>
                          <p className="text-truncate text-muted font-size-13">
                            {stats?.fraud_prescriptions.toLocaleString('fa-IR') || '0'} نسخه مشکوک شناسایی شد
                          </p>
                        </div>
                        <div className="flex-shrink-0 text-end me-3">
                          <h6 className="mb-1">{stats ? `${stats.fraud_percentage.toFixed(2)}%` : '0%'}</h6>
                          <div className="font-size-13">نرخ تقلب</div>
                        </div>
                      </div>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Dashboard;
