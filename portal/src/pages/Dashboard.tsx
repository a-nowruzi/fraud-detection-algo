import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, BarChart3, Activity, TrendingUp, Users, AlertTriangle, FileText, Clock, DollarSign } from 'lucide-react';
import ApiTester from '../components/ApiTester';

const Dashboard: React.FC = () => {

  return (
    <>
      <div className="row">
        <div className="col-xl-3 col-md-6">
          {/* card */}
          <div className="card card-h-100">
            {/* card body */}
            <div className="card-body">
              <div className="row align-items-center">
                <div className="col-6">
                  <span className="text-muted mb-3 lh-1 d-block text-truncate">کل نسخه‌ها</span>
                  <h4 className="mb-3">
                    <span className="counter-value" data-target="180000">180,000+</span>
                  </h4>
                </div>
                <div className="col-6">
                  <div className="text-center">
                    <Users className="h-8 w-8 text-primary" />
                  </div>
                </div>
              </div>
              <div className="text-nowrap">
                <span className="badge bg-success-subtle text-success">+2.5%</span>
                <span className="ms-1 text-muted font-size-13">از هفته گذشته</span>
              </div>
            </div>
          </div>
        </div>

        <div className="col-xl-3 col-md-6">
          {/* card */}
          <div className="card card-h-100">
            {/* card body */}
            <div className="card-body">
              <div className="row align-items-center">
                <div className="col-6">
                  <span className="text-muted mb-3 lh-1 d-block text-truncate">نسخه‌های مشکوک</span>
                  <h4 className="mb-3">
                    <span className="counter-value" data-target="36000">36,000+</span>
                  </h4>
                </div>
                <div className="col-6">
                  <div className="text-center">
                    <AlertTriangle className="h-8 w-8 text-warning" />
                  </div>
                </div>
              </div>
              <div className="text-nowrap">
                <span className="badge bg-danger-subtle text-danger">+5.2%</span>
                <span className="ms-1 text-muted font-size-13">از هفته گذشته</span>
              </div>
            </div>
          </div>
        </div>

        <div className="col-xl-3 col-md-6">
          {/* card */}
          <div className="card card-h-100">
            {/* card body */}
            <div className="card-body">
              <div className="row align-items-center">
                <div className="col-6">
                  <span className="text-muted mb-3 lh-1 d-block text-truncate">نرخ تشخیص</span>
                  <h4 className="mb-3">
                    <span className="counter-value" data-target="95">95</span>%
                  </h4>
                </div>
                <div className="col-6">
                  <div className="text-center">
                    <TrendingUp className="h-8 w-8 text-success" />
                  </div>
                </div>
              </div>
              <div className="text-nowrap">
                <span className="badge bg-success-subtle text-success">+1.2%</span>
                <span className="ms-1 text-muted font-size-13">از هفته گذشته</span>
              </div>
            </div>
          </div>
        </div>

        <div className="col-xl-3 col-md-6">
          {/* card */}
          <div className="card card-h-100">
            {/* card body */}
            <div className="card-body">
              <div className="row align-items-center">
                <div className="col-6">
                  <span className="text-muted mb-3 lh-1 d-block text-truncate">درآمد کل</span>
                  <h4 className="mb-3">
                    $<span className="counter-value" data-target="865.2">865.2</span>M
                  </h4>
                </div>
                <div className="col-6">
                  <div className="text-center">
                    <DollarSign className="h-8 w-8 text-info" />
                  </div>
                </div>
              </div>
              <div className="text-nowrap">
                <span className="badge bg-success-subtle text-success">+$20.9k</span>
                <span className="ms-1 text-muted font-size-13">از هفته گذشته</span>
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
                <h5 className="card-title me-2">نمودار تشخیص تقلب</h5>
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
                        <h5>نمودار تشخیص تقلب</h5>
                        <p className="text-muted">این نمودار آمار تشخیص تقلب را نمایش می‌دهد</p>
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
                          <span className="font-size-16">تشخیص مثبت</span>
                        </div>
                        <div className="flex-shrink-0">
                          <span className="badge rounded-pill bg-success-subtle text-success font-size-12 fw-medium">+2.5%</span>
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
                          <span className="font-size-16">تشخیص منفی</span>
                        </div>
                        <div className="flex-shrink-0">
                          <span className="badge rounded-pill bg-success-subtle text-success font-size-12 fw-medium">+8.3%</span>
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
                          <span className="font-size-16">در انتظار بررسی</span>
                        </div>
                        <div className="flex-shrink-0">
                          <span className="badge rounded-pill bg-danger-subtle text-danger font-size-12 fw-medium">-3.6%</span>
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
          {/* card */}
          <div className="card">
            {/* card body */}
            <div className="card-body">
              <div className="d-flex flex-wrap align-items-center mb-4">
                <h5 className="card-title me-2">آمار بر اساس نوع خدمت</h5>
                <div className="ms-auto">
                  <div className="dropdown">
                    <a className="dropdown-toggle text-reset" href="#" id="dropdownMenuButton1" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                      <span className="text-muted font-size-12">مرتب‌سازی:</span> <span className="fw-medium">همه<i className="mdi mdi-chevron-down ms-1"></i></span>
                    </a>

                    <div className="dropdown-menu dropdown-menu-end" aria-labelledby="dropdownMenuButton1">
                      <a className="dropdown-item" href="#">پزشکی عمومی</a>
                      <a className="dropdown-item" href="#">تخصصی</a>
                      <a className="dropdown-item" href="#">اورژانس</a>
                    </div>
                  </div>
                </div>
              </div>

              <div className="chart-placeholder" style={{ height: '250px', backgroundColor: '#f8f9fa', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '8px', marginBottom: '20px' }}>
                <div className="text-center">
                  <Activity className="h-12 w-12 text-muted mb-2" />
                  <h6>نمودار نوع خدمت</h6>
                </div>
              </div>

              <div className="px-2 py-2">
                <p className="mb-1">پزشکی عمومی <span className="float-end">75%</span></p>
                <div className="progress mt-2" style={{ height: '6px' }}>
                  <div className="progress-bar progress-bar-striped bg-primary" role="progressbar"
                    style={{ width: '75%' }} aria-valuenow={75} aria-valuemin={0} aria-valuemax={75}>
                  </div>
                </div>

                <p className="mt-3 mb-1">تخصصی <span className="float-end">55%</span></p>
                <div className="progress mt-2" style={{ height: '6px' }}>
                  <div className="progress-bar progress-bar-striped bg-primary" role="progressbar"
                    style={{ width: '55%' }} aria-valuenow={55} aria-valuemin={0} aria-valuemax={55}>
                  </div>
                </div>

                <p className="mt-3 mb-1">اورژانس <span className="float-end">85%</span></p>
                <div className="progress mt-2" style={{ height: '6px' }}>
                  <div className="progress-bar progress-bar-striped bg-primary" role="progressbar"
                    style={{ width: '85%' }} aria-valuenow={85} aria-valuemin={0} aria-valuemax={85}>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-xl-4">
          <div className="card">
            <div className="card-header align-items-center d-flex">
              <h4 className="card-title mb-0 flex-grow-1">امکانات سیستم</h4>
              <div className="flex-shrink-0">
                <ul className="nav nav-tabs-custom card-header-tabs" role="tablist">
                  <li className="nav-item">
                    <a className="nav-link active" data-bs-toggle="tab" href="#features-tab" role="tab">ویژگی‌ها</a>
                  </li>
                  <li className="nav-item">
                    <a className="nav-link" data-bs-toggle="tab" href="#howto-tab" role="tab">نحوه استفاده</a>
                  </li>
                </ul>
              </div>
            </div>

            <div className="card-body">
              <div className="tab-content">
                <div className="tab-pane active" id="features-tab" role="tabpanel">
                  <div className="space-y-3">
                    <div className="d-flex align-items-center">
                      <div className="avatar-sm me-3">
                        <span className="avatar-title rounded-circle bg-success-subtle text-success">
                          <Shield className="h-4 w-4" />
                        </span>
                      </div>
                      <div className="flex-grow-1">
                        <h6 className="mb-1">تشخیص تقلب</h6>
                        <p className="text-muted mb-0 font-size-13">با الگوریتم Isolation Forest</p>
                      </div>
                    </div>

                    <div className="d-flex align-items-center">
                      <div className="avatar-sm me-3">
                        <span className="avatar-title rounded-circle bg-primary-subtle text-primary">
                          <BarChart3 className="h-4 w-4" />
                        </span>
                      </div>
                      <div className="flex-grow-1">
                        <h6 className="mb-1">11 شاخص ریسک</h6>
                        <p className="text-muted mb-0 font-size-13">محاسبه دقیق شاخص‌های مختلف</p>
                      </div>
                    </div>

                    <div className="d-flex align-items-center">
                      <div className="avatar-sm me-3">
                        <span className="avatar-title rounded-circle bg-info-subtle text-info">
                          <FileText className="h-4 w-4" />
                        </span>
                      </div>
                      <div className="flex-grow-1">
                        <h6 className="mb-1">تاریخ شمسی</h6>
                        <p className="text-muted mb-0 font-size-13">پشتیبانی کامل از تاریخ شمسی</p>
                      </div>
                    </div>

                    <div className="text-center mt-3">
                      <Link to="/predict" className="btn btn-primary btn-sm">شروع کنید</Link>
                    </div>
                  </div>
                </div>

                <div className="tab-pane" id="howto-tab" role="tabpanel">
                  <div className="space-y-3">
                    <div className="d-flex align-items-start">
                      <div className="avatar-sm me-3">
                        <span className="avatar-title rounded-circle bg-primary font-size-16">1</span>
                      </div>
                      <div className="flex-grow-1">
                        <h6 className="mb-1">اطلاعات نسخه</h6>
                        <p className="text-muted mb-0 font-size-13">شماره بیمار، تاریخ‌ها و مبلغ را وارد کنید</p>
                      </div>
                    </div>

                    <div className="d-flex align-items-start">
                      <div className="avatar-sm me-3">
                        <span className="avatar-title rounded-circle bg-primary font-size-16">2</span>
                      </div>
                      <div className="flex-grow-1">
                        <h6 className="mb-1">تحلیل سیستم</h6>
                        <p className="text-muted mb-0 font-size-13">الگوریتم‌های هوشمند نسخه را بررسی می‌کنند</p>
                      </div>
                    </div>

                    <div className="d-flex align-items-start">
                      <div className="avatar-sm me-3">
                        <span className="avatar-title rounded-circle bg-primary font-size-16">3</span>
                      </div>
                      <div className="flex-grow-1">
                        <h6 className="mb-1">مشاهده نتیجه</h6>
                        <p className="text-muted mb-0 font-size-13">احتمال تقلب و شاخص‌های ریسک نمایش داده می‌شود</p>
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
            <div className="card-header align-items-center d-flex">
              <h4 className="card-title mb-0 flex-grow-1">آخرین فعالیت‌ها</h4>
            </div>

            <div className="card-body px-0">
              <div className="px-3" data-simplebar style={{ maxHeight: '352px' }}>
                <ul className="list-unstyled activity-wid mb-0">
                  <li className="activity-list activity-border">
                    <div className="activity-icon avatar-md">
                      <span className="avatar-title bg-warning-subtle text-warning rounded-circle">
                        <Shield className="font-size-24" />
                      </span>
                    </div>
                    <div className="timeline-list-item">
                      <div className="d-flex">
                        <div className="flex-grow-1 overflow-hidden me-4">
                          <h5 className="font-size-14 mb-1">24/05/2021, 18:24:56</h5>
                          <p className="text-truncate text-muted font-size-13">تشخیص تقلب جدید در نسخه شماره 12345</p>
                        </div>
                        <div className="flex-shrink-0 text-end me-3">
                          <h6 className="mb-1">+1 تراکنش</h6>
                          <div className="font-size-13">مشکوک</div>
                        </div>
                      </div>
                    </div>
                  </li>

                  <li className="activity-list activity-border">
                    <div className="activity-icon avatar-md">
                      <span className="avatar-title bg-primary-subtle text-primary rounded-circle">
                        <BarChart3 className="font-size-24" />
                      </span>
                    </div>
                    <div className="timeline-list-item">
                      <div className="d-flex">
                        <div className="flex-grow-1 overflow-hidden me-4">
                          <h5 className="font-size-14 mb-1">24/05/2021, 17:15:30</h5>
                          <p className="text-truncate text-muted font-size-13">گزارش ماهانه آماری تولید شد</p>
                        </div>
                        <div className="flex-shrink-0 text-end me-3">
                          <h6 className="mb-1">گزارش</h6>
                          <div className="font-size-13">تکمیل شد</div>
                        </div>
                      </div>
                    </div>
                  </li>

                  <li className="activity-list">
                    <div className="activity-icon avatar-md">
                      <span className="avatar-title bg-success-subtle text-success rounded-circle">
                        <Activity className="font-size-24" />
                      </span>
                    </div>
                    <div className="timeline-list-item">
                      <div className="d-flex">
                        <div className="flex-grow-1 overflow-hidden me-4">
                          <h5 className="font-size-14 mb-1">24/05/2021, 16:45:12</h5>
                          <p className="text-truncate text-muted font-size-13">بروزرسانی سیستم تشخیص تقلب</p>
                        </div>
                        <div className="flex-shrink-0 text-end me-3">
                          <h6 className="mb-1">بروزرسانی</h6>
                          <div className="font-size-13">موفق</div>
                        </div>
                      </div>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div className="col-xl-4">
          <div className="card">
            <div className="card-header align-items-center d-flex">
              <h4 className="card-title mb-0 flex-grow-1">آمار سریع</h4>
              <div className="flex-shrink-0">
                <div className="dropdown">
                  <a className="dropdown-toggle text-reset" href="#" id="dropdownMenuButton2" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    <span className="text-muted font-size-12">فیلتر:</span> <span className="fw-medium">امروز<i className="mdi mdi-chevron-down ms-1"></i></span>
                  </a>

                  <div className="dropdown-menu dropdown-menu-end" aria-labelledby="dropdownMenuButton2">
                    <a className="dropdown-item" href="#">امروز</a>
                    <a className="dropdown-item" href="#">هفته</a>
                    <a className="dropdown-item" href="#">ماه</a>
                  </div>
                </div>
              </div>
            </div>

            <div className="card-body">
              <div className="space-y-4">
                <div className="d-flex align-items-center">
                  <div className="flex-shrink-0 me-3">
                    <div className="avatar-sm">
                      <span className="avatar-title rounded-circle bg-primary-subtle text-primary">
                        <Users className="h-4 w-4" />
                      </span>
                    </div>
                  </div>
                  <div className="flex-grow-1">
                    <h6 className="mb-1">کاربران فعال</h6>
                    <p className="text-muted mb-0">1,234 کاربر</p>
                  </div>
                  <div className="flex-shrink-0">
                    <span className="badge bg-success-subtle text-success">+12%</span>
                  </div>
                </div>

                <div className="d-flex align-items-center">
                  <div className="flex-shrink-0 me-3">
                    <div className="avatar-sm">
                      <span className="avatar-title rounded-circle bg-warning-subtle text-warning">
                        <Clock className="h-4 w-4" />
                      </span>
                    </div>
                  </div>
                  <div className="flex-grow-1">
                    <h6 className="mb-1">زمان پاسخ</h6>
                    <p className="text-muted mb-0">2.3 ثانیه</p>
                  </div>
                  <div className="flex-shrink-0">
                    <span className="badge bg-success-subtle text-success">-5%</span>
                  </div>
                </div>

                <div className="d-flex align-items-center">
                  <div className="flex-shrink-0 me-3">
                    <div className="avatar-sm">
                      <span className="avatar-title rounded-circle bg-info-subtle text-info">
                        <TrendingUp className="h-4 w-4" />
                      </span>
                    </div>
                  </div>
                  <div className="flex-grow-1">
                    <h6 className="mb-1">دقت تشخیص</h6>
                    <p className="text-muted mb-0">95.2%</p>
                  </div>
                  <div className="flex-shrink-0">
                    <span className="badge bg-success-subtle text-success">+2.1%</span>
                  </div>
                </div>
              </div>

              <div className="text-center mt-4">
                <Link to="/stats" className="btn btn-primary btn-sm">
                  مشاهده جزئیات <i className="mdi mdi-arrow-right ms-1"></i>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* API Tester */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h4 className="card-title">تست API</h4>
            </div>
            <div className="card-body">
              <ApiTester />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Dashboard;
