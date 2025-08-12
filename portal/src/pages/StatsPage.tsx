import React, { useState, useEffect, useRef } from 'react';
import { apiService, type SystemStats } from '../services/api';

// تعریف نوع ApexCharts برای TypeScript
declare global {
  interface Window {
    ApexCharts: any;
  }
}

const StatsPage: React.FC = () => {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartsReady, setChartsReady] = useState(false);
  const systemPerformanceChartRef = useRef<HTMLDivElement>(null);
  const prescriptionDistributionChartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchStats();
    checkApexCharts();
  }, []);

  useEffect(() => {
    if (stats && chartsReady && systemPerformanceChartRef.current && prescriptionDistributionChartRef.current) {
      initializeCharts();
    }
  }, [stats, chartsReady]);

  const checkApexCharts = () => {
    const checkInterval = setInterval(() => {
      if (window.ApexCharts) {
        setChartsReady(true);
        clearInterval(checkInterval);
      }
    }, 100);

    // توقف بررسی بعد از 5 ثانیه
    setTimeout(() => {
      clearInterval(checkInterval);
      if (!window.ApexCharts) {
        console.warn('ApexCharts بارگذاری نشد');
      }
    }, 5000);
  };

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

  const initializeCharts = () => {
    if (!stats) return;

    // تاخیر کوتاه برای اطمینان از بارگذاری کامل ApexCharts
    setTimeout(() => {
      // نمودار عملکرد سیستم
      if (systemPerformanceChartRef.current && window.ApexCharts) {
        const systemPerformanceOptions = {
          series: [{
            name: 'نسخه‌های سالم',
            data: [stats.normal_prescriptions]
          }, {
            name: 'نسخه‌های مشکوک',
            data: [stats.fraud_prescriptions]
          }, {
            name: 'کل نسخه‌ها',
            data: [stats.total_prescriptions]
          }],
          chart: {
            type: 'bar',
            height: 350,
            toolbar: {
              show: false
            },
            fontFamily: 'Estedad, sans-serif'
          },
          plotOptions: {
            bar: {
              horizontal: false,
              columnWidth: '55%',
              endingShape: 'rounded'
            },
          },
          dataLabels: {
            enabled: false
          },
          stroke: {
            show: true,
            width: 2,
            colors: ['transparent']
          },
          xaxis: {
            categories: ['آمار نسخه‌ها'],
            labels: {
              style: {
                fontFamily: 'Estedad, sans-serif'
              }
            }
          },
          yaxis: {
            title: {
              text: 'تعداد نسخه‌ها',
              style: {
                fontFamily: 'Estedad, sans-serif'
              }
            },
            labels: {
              style: {
                fontFamily: 'Estedad, sans-serif'
              }
            }
          },
          fill: {
            opacity: 1
          },
          tooltip: {
            y: {
              formatter: function (val: number) {
                return val.toLocaleString('fa-IR') + " نسخه"
              }
            }
          },
          colors: ['#34c38f', '#f46a6a', '#5156be'],
          legend: {
            fontFamily: 'Estedad, sans-serif',
            labels: {
              colors: '#6c757d'
            }
          }
        };

        // حذف نمودار قبلی اگر وجود دارد
        if (systemPerformanceChartRef.current.querySelector('.apexcharts-canvas')) {
          systemPerformanceChartRef.current.innerHTML = '';
        }

        try {
          const chart = new window.ApexCharts(systemPerformanceChartRef.current, systemPerformanceOptions);
          chart.render();
        } catch (error) {
          console.error('خطا در ایجاد نمودار عملکرد سیستم:', error);
        }
      }

      // نمودار توزیع نسخه‌ها
      if (prescriptionDistributionChartRef.current && window.ApexCharts) {
        const prescriptionDistributionOptions = {
          series: [stats.normal_prescriptions, stats.fraud_prescriptions],
          chart: {
            type: 'donut',
            height: 250,
            fontFamily: 'Estedad, sans-serif'
          },
          labels: ['نسخه‌های سالم', 'نسخه‌های مشکوک'],
          colors: ['#34c38f', '#f46a6a'],
          plotOptions: {
            pie: {
              donut: {
                size: '70%'
              }
            }
          },
          dataLabels: {
            enabled: true,
            formatter: function (val: number, opts: any) {
              return opts.w.globals.seriesTotals[opts.seriesIndex].toLocaleString('fa-IR');
            },
            style: {
              fontFamily: 'Estedad, sans-serif',
              fontSize: '12px'
            }
          },
          legend: {
            position: 'bottom',
            fontFamily: 'Estedad, sans-serif',
            labels: {
              colors: '#6c757d'
            }
          },
          tooltip: {
            y: {
              formatter: function (val: number) {
                return val.toLocaleString('fa-IR') + " نسخه";
              }
            }
          }
        };

        // حذف نمودار قبلی اگر وجود دارد
        if (prescriptionDistributionChartRef.current.querySelector('.apexcharts-canvas')) {
          prescriptionDistributionChartRef.current.innerHTML = '';
        }

        try {
          const chart = new window.ApexCharts(prescriptionDistributionChartRef.current, prescriptionDistributionOptions);
          chart.render();
        } catch (error) {
          console.error('خطا در ایجاد نمودار توزیع نسخه‌ها:', error);
        }
      }
    }, 100);
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
        <button onClick={fetchStats} className="btn btn-primary">
          <i className="mdi mdi-refresh me-2"></i>
          تلاش مجدد
        </button>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  if (!chartsReady) {
    return (
      <div className="text-center p-5">
        <div className="alert alert-warning mb-4" role="alert">
          <i className="mdi mdi-chart-line me-2"></i>
          در حال بارگذاری نمودارها...
        </div>
        <div className="spinner-border text-warning" role="status">
          <span className="visually-hidden">بارگذاری نمودارها...</span>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'کل نسخه‌ها',
      value: stats.total_prescriptions.toLocaleString('fa-IR'),
      icon: 'mdi mdi-database',
      color: 'primary',
      bgColor: 'primary-subtle',
      textColor: 'primary',
      changeType: 'success',
    },
    {
      title: 'نسخه‌های سالم',
      value: stats.normal_prescriptions.toLocaleString('fa-IR'),
      icon: 'mdi mdi-check-circle',
      color: 'success',
      bgColor: 'success-subtle',
      textColor: 'success',
      changeType: 'success',
    },
    {
      title: 'نسخه‌های مشکوک',
      value: stats.fraud_prescriptions.toLocaleString('fa-IR'),
      icon: 'mdi mdi-alert-triangle',
      color: 'danger',
      bgColor: 'danger-subtle',
      textColor: 'danger',
      changeType: 'danger',
    },
    {
      title: 'درصد تقلب',
      value: `${stats.fraud_percentage.toFixed(2)}%`,
      icon: 'mdi mdi-trending-up',
      color: 'warning',
      bgColor: 'warning-subtle',
      textColor: 'warning',
      changeType: 'success'
    },
  ];

  return (
    <>
      {/* کارت‌های آمار */}
      <div className="row">
        {statCards.map((card, index) => (
          <div key={index} className="col-xl-3 col-md-6">
            <div className="card card-h-100">
              <div className="card-body">
                <div className="row align-items-center">
                  <div className="col-12">
                    <span className="text-muted mb-3 lh-1 d-block text-truncate">{card.title}</span>
                    <h4 className="mb-3">
                      <span className="counter-value" data-target={card.value.replace(/,/g, '')}>{card.value}</span>
                    </h4>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* نمودار اصلی */}
      <div className="row">
        <div className="col-xl-8">
          <div className="card">
            <div className="card-body">
              <div className="d-flex flex-wrap align-items-center mb-4">
                <h5 className="card-title me-2">نمودار عملکرد سیستم</h5>
              </div>
              <div className="row align-items-center">
                <div className="col-xl-8">
                  <div>
                    <div ref={systemPerformanceChartRef} className="apex-charts"></div>
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
                            +{((stats.normal_prescriptions / stats.total_prescriptions) * 100).toFixed(1)}%
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
                            {((stats.fraud_prescriptions / stats.total_prescriptions) * 100).toFixed(1)}%
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
                          <span className="font-size-16">کل پردازش شده</span>
                        </div>
                        <div className="flex-shrink-0">
                          <span className="badge rounded-pill bg-primary-subtle text-primary font-size-12 fw-medium">
                            {stats.total_prescriptions.toLocaleString('fa-IR')}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-xl-4">
          <div className="card">
            <div className="card-body">
              <div className="d-flex flex-wrap align-items-center mb-4">
                <h5 className="card-title me-2">توزیع نسخه‌ها</h5>
              </div>
              <div ref={prescriptionDistributionChartRef} style={{ height: '250px' }}></div>
              <div className="px-2 py-2">
                <p className="mb-1">نسخه‌های سالم <span className="float-end">
                  {((stats.normal_prescriptions / stats.total_prescriptions) * 100).toFixed(1)}%
                </span></p>
                <div className="progress mt-2" style={{ height: '6px' }}>
                  <div className="progress-bar progress-bar-striped bg-success" role="progressbar"
                    style={{ width: `${(stats.normal_prescriptions / stats.total_prescriptions) * 100}%` }}
                    aria-valuenow={(stats.normal_prescriptions / stats.total_prescriptions) * 100}
                    aria-valuemin={0} aria-valuemax={100}>
                  </div>
                </div>

                <p className="mt-3 mb-1">نسخه‌های مشکوک <span className="float-end">
                  {((stats.fraud_prescriptions / stats.total_prescriptions) * 100).toFixed(1)}%
                </span></p>
                <div className="progress mt-2" style={{ height: '6px' }}>
                  <div className="progress-bar progress-bar-striped bg-danger" role="progressbar"
                    style={{ width: `${(stats.fraud_prescriptions / stats.total_prescriptions) * 100}%` }}
                    aria-valuenow={(stats.fraud_prescriptions / stats.total_prescriptions) * 100}
                    aria-valuemin={0} aria-valuemax={100}>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default StatsPage;
