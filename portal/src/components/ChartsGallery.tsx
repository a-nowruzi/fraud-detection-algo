import React, { useState } from 'react';
import { apiService } from '../services/api';
import { BarChart3, PieChart, TrendingUp, MapPin, Users, Calendar, CreditCard, FileText, Activity, AlertTriangle } from 'lucide-react';

const ChartsGallery: React.FC = () => {
  const [selectedChart, setSelectedChart] = useState<string | null>(null);
  const [chartData, setChartData] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const charts = [
    // نمودارهای اصلی
    {
      id: 'fraud-by-province',
      title: 'تقلب بر اساس استان',
      description: 'نمودار میله‌ای از تعداد نسخه‌های تقلبی در هر استان',
      icon: MapPin,
      category: 'جغرافیایی',
    },
    {
      id: 'fraud-by-gender',
      title: 'تقلب بر اساس جنسیت',
      description: 'نمودار دایره‌ای از نسبت نسخه‌های تقلبی بر اساس جنسیت',
      icon: Users,
      category: 'جمعیت‌شناسی',
    },
    {
      id: 'fraud-by-age',
      title: 'تقلب بر اساس گروه سنی',
      description: 'نمودار دایره‌ای از نسبت نسخه‌های تقلبی بر اساس گروه سنی',
      icon: Users,
      category: 'جمعیت‌شناسی',
    },
    {
      id: 'fraud-ratio-by-age-group',
      title: 'نسبت تقلب بر اساس گروه سنی',
      description: 'نمودار میله‌ای از نسبت نسخه‌های تقلبی در هر گروه سنی',
      icon: BarChart3,
      category: 'جمعیت‌شناسی',
    },
    {
      id: 'province-fraud-ratio',
      title: 'نسبت تقلب بر اساس استان',
      description: 'نمودار میله‌ای از نسبت نسخه‌های تقلبی در هر استان',
      icon: MapPin,
      category: 'جغرافیایی',
    },
    {
      id: 'province-gender-fraud-percentage',
      title: 'درصد تقلب بر اساس استان و جنسیت',
      description: 'نمودار میله‌ای از درصد نسخه‌های تقلبی در هر استان بر حسب جنسیت',
      icon: BarChart3,
      category: 'تحلیلی',
    },
    {
      id: 'fraud-counts-by-date',
      title: 'تعداد تقلب بر اساس تاریخ',
      description: 'نمودار خطی از تعداد نسخه‌های تقلبی بر حسب تاریخ پذیرش',
      icon: Calendar,
      category: 'زمانی',
    },
    {
      id: 'fraud-ratio-by-date',
      title: 'نسبت تقلب بر اساس تاریخ',
      description: 'نمودار خطی از نسبت نسخه‌های تقلبی بر حسب تاریخ پذیرش',
      icon: TrendingUp,
      category: 'زمانی',
    },
    {
      id: 'fraud-ratio-by-ins-cover',
      title: 'نسبت تقلب بر اساس پوشش بیمه',
      description: 'نمودار میله‌ای از نسبت نسخه‌های تقلبی بر اساس نوع پوشش بیمه',
      icon: CreditCard,
      category: 'بیمه',
    },
    {
      id: 'fraud-ratio-by-invoice-type',
      title: 'نسبت تقلب بر اساس نوع فاکتور',
      description: 'نمودار میله‌ای از نسبت نسخه‌های تقلبی بر اساس نوع فاکتور',
      icon: FileText,
      category: 'اداری',
    },
    {
      id: 'fraud-ratio-by-medical-record-type',
      title: 'نسبت تقلب بر اساس نوع پرونده',
      description: 'نمودار میله‌ای از نسبت نسخه‌های تقلبی بر اساس نوع پرونده پزشکی',
      icon: FileText,
      category: 'اداری',
    },
    {
      id: 'provider-risk-indicator',
      title: 'شاخص ریسک پزشک',
      description: 'نمودار شاخص ریسک برای پزشک خاص در طول زمان',
      icon: Activity,
      category: 'شاخص‌های ریسک',
      requiresParams: true,
      params: [
        { name: 'provider_name', label: 'نام پزشک', type: 'text', placeholder: 'نام پزشک را وارد کنید' },
        { name: 'indicator', label: 'نوع شاخص', type: 'select', options: ['cost', 'frequency', 'pattern'] }
      ]
    },
    {
      id: 'patient-risk-indicator',
      title: 'شاخص ریسک بیمار',
      description: 'نمودار شاخص ریسک برای بیمار خاص در طول زمان',
      icon: AlertTriangle,
      category: 'شاخص‌های ریسک',
      requiresParams: true,
      params: [
        { name: 'patient_id', label: 'شماره بیمار', type: 'number', placeholder: 'شماره بیمار را وارد کنید' },
        { name: 'indicator', label: 'نوع شاخص', type: 'select', options: ['cost', 'frequency', 'pattern'] }
      ]
    },
  ];

  const fetchChart = async (chartId: string, params?: any) => {
    setLoading(true);
    setError(null);
    setSelectedChart(chartId);

    try {
      let response;
      switch (chartId) {
        case 'fraud-by-province':
          response = await apiService.getFraudByProvinceChart();
          break;
        case 'fraud-by-gender':
          response = await apiService.getFraudByGenderChart();
          break;
        case 'fraud-by-age':
          response = await apiService.getFraudByAgeChart();
          break;
        case 'fraud-ratio-by-age-group':
          response = await apiService.getFraudRatioByAgeGroupChart();
          break;
        case 'province-fraud-ratio':
          response = await apiService.getProvinceFraudRatioChart();
          break;
        case 'province-gender-fraud-percentage':
          response = await apiService.getProvinceGenderFraudPercentageChart();
          break;
        case 'fraud-counts-by-date':
          response = await apiService.getFraudCountsByDateChart();
          break;
        case 'fraud-ratio-by-date':
          response = await apiService.getFraudRatioByDateChart();
          break;
        case 'fraud-ratio-by-ins-cover':
          response = await apiService.getFraudRatioByInsCoverChart();
          break;
        case 'fraud-ratio-by-invoice-type':
          response = await apiService.getFraudRatioByInvoiceTypeChart();
          break;
        case 'fraud-ratio-by-medical-record-type':
          response = await apiService.getFraudRatioByMedicalRecordTypeChart();
          break;
        case 'provider-risk-indicator':
          if (params?.provider_name && params?.indicator) {
            response = await apiService.getProviderRiskIndicatorChart(params.provider_name, params.indicator);
          } else {
            throw new Error('لطفاً نام پزشک و نوع شاخص را وارد کنید');
          }
          break;
        case 'patient-risk-indicator':
          if (params?.patient_id && params?.indicator) {
            response = await apiService.getPatientRiskIndicatorChart(Number(params.patient_id), params.indicator);
          } else {
            throw new Error('لطفاً شماره بیمار و نوع شاخص را وارد کنید');
          }
          break;
        default:
          throw new Error('نمودار مورد نظر یافت نشد');
      }
      setChartData(response.chart);
    } catch (err) {
      setError('خطا در دریافت نمودار');
      console.error('Chart error:', err);
    } finally {
      setLoading(false);
    }
  };

  const categories = Array.from(new Set(charts.map(chart => chart.category)));
  const filteredCharts = selectedCategory 
    ? charts.filter(chart => chart.category === selectedCategory)
    : charts;

  const [chartParams, setChartParams] = useState<Record<string, any>>({});

  const handleParamChange = (chartId: string, paramName: string, value: any) => {
    setChartParams(prev => ({
      ...prev,
      [chartId]: {
        ...prev[chartId],
        [paramName]: value
      }
    }));
  };

  const handleChartClick = (chart: any) => {
    if (chart.requiresParams) {
      // For charts that require parameters, we'll show a modal or form
      // For now, we'll just set the selected chart and let user fill params
      setSelectedChart(chart.id);
    } else {
      fetchChart(chart.id);
    }
  };

  const renderChartParams = (chart: any) => {
    if (!chart.requiresParams) return null;

    return (
      <div className="p-4 bg-gray-50 rounded-lg mb-4">
        <h4 className="font-medium text-gray-900 mb-3">پارامترهای مورد نیاز</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {chart.params.map((param: any) => (
            <div key={param.name}>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {param.label}
              </label>
              {param.type === 'select' ? (
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  onChange={(e) => handleParamChange(chart.id, param.name, e.target.value)}
                >
                  <option value="">انتخاب کنید</option>
                  {param.options.map((option: string) => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              ) : (
                <input
                  type={param.type}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder={param.placeholder}
                  onChange={(e) => handleParamChange(chart.id, param.name, e.target.value)}
                />
              )}
            </div>
          ))}
        </div>
        <button
          onClick={() => fetchChart(chart.id, chartParams[chart.id])}
          className="mt-3 btn-primary"
          disabled={!chartParams[chart.id] || Object.values(chartParams[chart.id] || {}).some(v => !v)}
        >
          نمایش نمودار
        </button>
      </div>
    );
  };

  return (
    <div className="space-y-6">

      {/* فیلتر دسته‌بندی */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSelectedCategory(null)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            !selectedCategory
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          همه
        </button>
        {categories.map(category => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedCategory === category
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {category}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* لیست نمودارها */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">نمودارهای موجود</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {filteredCharts.map(chart => (
              <div
                key={chart.id}
                onClick={() => handleChartClick(chart)}
                className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                  selectedChart === chart.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-start">
                  <chart.icon className="h-5 w-5 text-gray-500 mt-0.5 ml-3" />
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{chart.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{chart.description}</p>
                    <div className="flex items-center mt-2 gap-2">
                      <span className="inline-block px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                        {chart.category}
                      </span>
                      {chart.requiresParams && (
                        <span className="inline-block px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-700 rounded">
                          نیاز به پارامتر
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* نمایش نمودار */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">پیش‌نمایش نمودار</h3>
          <div className="bg-white rounded-lg border border-gray-200 p-4 min-h-96 flex items-center justify-center">
            {loading ? (
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                <p className="text-gray-600">در حال بارگذاری نمودار...</p>
              </div>
            ) : error ? (
              <div className="text-center">
                <div className="text-red-600 mb-4">{error}</div>
                <button
                  onClick={() => selectedChart && fetchChart(selectedChart, chartParams[selectedChart])}
                  className="btn-primary"
                >
                  تلاش مجدد
                </button>
              </div>
            ) : chartData ? (
              <div className="w-full">
                <img
                  src={`data:image/png;base64,${chartData}`}
                  alt="نمودار"
                  className="w-full h-auto rounded-lg shadow-sm"
                />
              </div>
            ) : (
              <div className="text-center text-gray-500">
                <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>برای مشاهده نمودار، یکی از موارد بالا را انتخاب کنید</p>
              </div>
            )}
          </div>

          {/* نمایش پارامترها برای نمودارهای انتخاب شده */}
          {selectedChart && charts.find(c => c.id === selectedChart)?.requiresParams && (
            renderChartParams(charts.find(c => c.id === selectedChart)!)
          )}
        </div>
      </div>
    </div>
  );
};

export default ChartsGallery;
