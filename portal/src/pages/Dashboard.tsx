import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, BarChart3, Activity, Plus, TrendingUp, Users, AlertTriangle } from 'lucide-react';
import ApiTester from '../components/ApiTester';

const Dashboard: React.FC = () => {
  const features = [
    {
      title: 'تشخیص تقلب',
      description: 'بررسی نسخه‌های پزشکی و تشخیص احتمال تقلب',
      icon: Shield,
      href: '/predict',
      color: 'bg-blue-500',
    },
    {
      title: 'نمودارها',
      description: 'مشاهده نمودارهای تحلیلی مختلف',
      icon: BarChart3,
      href: '/charts',
      color: 'bg-green-500',
    },
    {
      title: 'آمار سیستم',
      description: 'مشاهده آمار کلی و عملکرد سیستم',
      icon: Activity,
      href: '/stats',
      color: 'bg-purple-500',
    },
  ];

  const quickStats = [
    {
      title: 'کل نسخه‌ها',
      value: '180,000+',
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'نسخه‌های مشکوک',
      value: '36,000+',
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
    },
    {
      title: 'نرخ تشخیص',
      value: '95%',
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          خوش آمدید به سیستم تشخیص تقلب پزشکی
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          این سیستم با استفاده از الگوریتم‌های پیشرفته یادگیری ماشین، 
          نسخه‌های پزشکی را بررسی کرده و احتمال تقلب را تشخیص می‌دهد.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {quickStats.map((stat, index) => (
          <div key={index} className="card">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${stat.bgColor} ${stat.color}`}>
                <stat.icon className="h-6 w-6" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Features */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">امکانات سیستم</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <Link
              key={index}
              to={feature.href}
              className="card hover:shadow-lg transition-shadow duration-200 group"
            >
              <div className="flex items-center mb-4">
                <div className={`p-3 rounded-lg ${feature.color} text-white group-hover:scale-110 transition-transform duration-200`}>
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mr-3">{feature.title}</h3>
              </div>
              <p className="text-gray-600 mb-4">{feature.description}</p>
              <div className="flex items-center text-primary-600 font-medium">
                <span>شروع کنید</span>
                <Plus className="h-4 w-4 mr-2" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* System Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">ویژگی‌های کلیدی</h3>
          <ul className="space-y-3">
            <li className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full ml-3"></div>
              <span>تشخیص تقلب با الگوریتم Isolation Forest</span>
            </li>
            <li className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full ml-3"></div>
              <span>محاسبه ۱۱ شاخص ریسک مختلف</span>
            </li>
            <li className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full ml-3"></div>
              <span>نمودارهای تحلیلی متنوع</span>
            </li>
            <li className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full ml-3"></div>
              <span>پشتیبانی از تاریخ شمسی</span>
            </li>
            <li className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full ml-3"></div>
              <span>رابط کاربری فارسی و کاربرپسند</span>
            </li>
          </ul>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">نحوه استفاده</h3>
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold ml-3 mt-0.5">
                1
              </div>
              <div>
                <h4 className="font-medium text-gray-900">اطلاعات نسخه را وارد کنید</h4>
                <p className="text-sm text-gray-600">شماره بیمار، تاریخ‌ها، نوع خدمت و مبلغ را وارد کنید</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold ml-3 mt-0.5">
                2
              </div>
              <div>
                <h4 className="font-medium text-gray-900">سیستم تحلیل می‌کند</h4>
                <p className="text-sm text-gray-600">الگوریتم‌های هوشمند نسخه را بررسی می‌کنند</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold ml-3 mt-0.5">
                3
              </div>
              <div>
                <h4 className="font-medium text-gray-900">نتیجه را مشاهده کنید</h4>
                <p className="text-sm text-gray-600">احتمال تقلب و شاخص‌های ریسک نمایش داده می‌شود</p>
              </div>
            </div>
          </div>
        </div>
      </div>

             {/* API Tester */}
       <div className="mt-8">
         <ApiTester />
       </div>

       {/* CTA */}
       <div className="text-center mt-8">
         <Link
           to="/predict"
           className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200"
         >
           <Shield className="ml-2 h-5 w-5" />
           شروع تشخیص تقلب
         </Link>
       </div>
     </div>
   );
 };

export default Dashboard;
