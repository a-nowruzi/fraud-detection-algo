import React, { useState } from 'react';
import { apiService, type PrescriptionData } from '../services/api';
import { Play, CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface ApiEndpoint {
  name: string;
  method: 'GET' | 'POST';
  path: string;
  description: string;
  requiresParams: boolean;
  params?: Array<{
    name: string;
    label: string;
    type: 'text' | 'number' | 'select';
    placeholder?: string;
    options?: string[];
    required?: boolean;
  }>;
}

const ApiTester: React.FC = () => {
  const [selectedEndpoint, setSelectedEndpoint] = useState<string | null>(null);
  const [params, setParams] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  const endpoints: ApiEndpoint[] = [
    {
      name: 'getStats',
      method: 'GET',
      path: '/stats',
      description: 'دریافت آمار کلی سیستم',
      requiresParams: false,
    },
    {
      name: 'getModelInfo',
      method: 'GET',
      path: '/model-info',
      description: 'دریافت اطلاعات مدل',
      requiresParams: false,
    },
    {
      name: 'predictFraud',
      method: 'POST',
      path: '/predict',
      description: 'پیش‌بینی تقلب برای نسخه جدید',
      requiresParams: true,
      params: [
        { name: 'ID', label: 'شماره بیمار', type: 'number', required: true, placeholder: '48928' },
        { name: 'jalali_date', label: 'تاریخ تولد (شمسی)', type: 'text', required: true, placeholder: '1361/05/04' },
        { name: 'Adm_date', label: 'تاریخ پذیرش (شمسی)', type: 'text', required: true, placeholder: '1403/08/05' },
        { name: 'Service', label: 'نوع خدمت', type: 'text', required: true, placeholder: 'ویزیت متخصص' },
        { name: 'provider_name', label: 'نام پزشک', type: 'text', required: true, placeholder: 'حسینخان خسروخاور' },
        { name: 'provider_specialty', label: 'تخصص پزشک', type: 'text', required: true, placeholder: 'دکترای حرفه‌ای پزشکی' },
        { name: 'cost_amount', label: 'مبلغ (ریال)', type: 'number', required: true, placeholder: '2000000' },
      ],
    },
    {
      name: 'getFraudByProvinceChart',
      method: 'GET',
      path: '/charts/fraud-by-province',
      description: 'نمودار تقلب بر اساس استان',
      requiresParams: false,
    },
    {
      name: 'getFraudByGenderChart',
      method: 'GET',
      path: '/charts/fraud-by-gender',
      description: 'نمودار تقلب بر اساس جنسیت',
      requiresParams: false,
    },
    {
      name: 'getFraudByAgeChart',
      method: 'GET',
      path: '/charts/fraud-by-age',
      description: 'نمودار تقلب بر اساس گروه سنی',
      requiresParams: false,
    },
    {
      name: 'getFraudRatioByAgeGroupChart',
      method: 'GET',
      path: '/charts/fraud-ratio-by-age-group',
      description: 'نسبت تقلب بر اساس گروه سنی',
      requiresParams: false,
    },
    {
      name: 'getProvinceFraudRatioChart',
      method: 'GET',
      path: '/charts/province-fraud-ratio',
      description: 'نسبت تقلب بر اساس استان',
      requiresParams: false,
    },
    {
      name: 'getProvinceGenderFraudPercentageChart',
      method: 'GET',
      path: '/charts/province-gender-fraud-percentage',
      description: 'درصد تقلب بر اساس استان و جنسیت',
      requiresParams: false,
    },
    {
      name: 'getFraudCountsByDateChart',
      method: 'GET',
      path: '/charts/fraud-counts-by-date',
      description: 'تعداد تقلب بر اساس تاریخ',
      requiresParams: false,
    },
    {
      name: 'getFraudRatioByDateChart',
      method: 'GET',
      path: '/charts/fraud-ratio-by-date',
      description: 'نسبت تقلب بر اساس تاریخ',
      requiresParams: false,
    },
    {
      name: 'getFraudRatioByInsCoverChart',
      method: 'GET',
      path: '/charts/fraud-ratio-by-ins-cover',
      description: 'نسبت تقلب بر اساس پوشش بیمه',
      requiresParams: false,
    },
    {
      name: 'getFraudRatioByInvoiceTypeChart',
      method: 'GET',
      path: '/charts/fraud-ratio-by-invoice-type',
      description: 'نسبت تقلب بر اساس نوع فاکتور',
      requiresParams: false,
    },
    {
      name: 'getFraudRatioByMedicalRecordTypeChart',
      method: 'GET',
      path: '/charts/fraud-ratio-by-medical-record-type',
      description: 'نسبت تقلب بر اساس نوع پرونده',
      requiresParams: false,
    },
    {
      name: 'getRiskIndicatorsChart',
      method: 'POST',
      path: '/charts/risk-indicators',
      description: 'نمودار شاخص‌های ریسک',
      requiresParams: true,
      params: [
        { name: 'ID', label: 'شماره بیمار', type: 'number', required: true, placeholder: '48928' },
        { name: 'jalali_date', label: 'تاریخ تولد (شمسی)', type: 'text', required: true, placeholder: '1361/05/04' },
        { name: 'Adm_date', label: 'تاریخ پذیرش (شمسی)', type: 'text', required: true, placeholder: '1403/08/05' },
        { name: 'Service', label: 'نوع خدمت', type: 'text', required: true, placeholder: 'ویزیت متخصص' },
        { name: 'provider_name', label: 'نام پزشک', type: 'text', required: true, placeholder: 'حسینخان خسروخاور' },
        { name: 'provider_specialty', label: 'تخصص پزشک', type: 'text', required: true, placeholder: 'دکترای حرفه‌ای پزشکی' },
        { name: 'cost_amount', label: 'مبلغ (ریال)', type: 'number', required: true, placeholder: '2000000' },
      ],
    },
    {
      name: 'getProviderRiskIndicatorChart',
      method: 'GET',
      path: '/charts/provider-risk-indicator',
      description: 'شاخص ریسک پزشک',
      requiresParams: true,
      params: [
        { name: 'provider_name', label: 'نام پزشک', type: 'text', required: true, placeholder: 'نام پزشک' },
        { name: 'indicator', label: 'نوع شاخص', type: 'select', required: true, options: ['cost', 'frequency', 'pattern'] },
      ],
    },
    {
      name: 'getPatientRiskIndicatorChart',
      method: 'GET',
      path: '/charts/patient-risk-indicator',
      description: 'شاخص ریسک بیمار',
      requiresParams: true,
      params: [
        { name: 'patient_id', label: 'شماره بیمار', type: 'number', required: true, placeholder: '48928' },
        { name: 'indicator', label: 'نوع شاخص', type: 'select', required: true, options: ['cost', 'frequency', 'pattern'] },
      ],
    },
  ];

  const handleParamChange = (endpointName: string, paramName: string, value: any) => {
    setParams(prev => ({
      ...prev,
      [endpointName]: {
        ...prev[endpointName],
        [paramName]: value
      }
    }));
  };

  const testEndpoint = async (endpoint: ApiEndpoint) => {
    setLoading(true);
    setSelectedEndpoint(endpoint.name);
    setErrors(prev => ({ ...prev, [endpoint.name]: '' }));

    try {
      let result;
      const endpointParams = params[endpoint.name] || {};

      switch (endpoint.name) {
        case 'getStats':
          result = await apiService.getStats();
          break;
        case 'getModelInfo':
          result = await apiService.getModelInfo();
          break;
        case 'predictFraud':
          const prescriptionData: PrescriptionData = {
            ID: Number(endpointParams.ID),
            jalali_date: endpointParams.jalali_date,
            Adm_date: endpointParams.Adm_date,
            Service: endpointParams.Service,
            provider_name: endpointParams.provider_name,
            provider_specialty: endpointParams.provider_specialty,
            cost_amount: Number(endpointParams.cost_amount),
          };
          result = await apiService.predictFraud(prescriptionData);
          break;
        case 'getFraudByProvinceChart':
          result = await apiService.getFraudByProvinceChart();
          break;
        case 'getFraudByGenderChart':
          result = await apiService.getFraudByGenderChart();
          break;
        case 'getFraudByAgeChart':
          result = await apiService.getFraudByAgeChart();
          break;
        case 'getFraudRatioByAgeGroupChart':
          result = await apiService.getFraudRatioByAgeGroupChart();
          break;
        case 'getProvinceFraudRatioChart':
          result = await apiService.getProvinceFraudRatioChart();
          break;
        case 'getProvinceGenderFraudPercentageChart':
          result = await apiService.getProvinceGenderFraudPercentageChart();
          break;
        case 'getFraudCountsByDateChart':
          result = await apiService.getFraudCountsByDateChart();
          break;
        case 'getFraudRatioByDateChart':
          result = await apiService.getFraudRatioByDateChart();
          break;
        case 'getFraudRatioByInsCoverChart':
          result = await apiService.getFraudRatioByInsCoverChart();
          break;
        case 'getFraudRatioByInvoiceTypeChart':
          result = await apiService.getFraudRatioByInvoiceTypeChart();
          break;
        case 'getFraudRatioByMedicalRecordTypeChart':
          result = await apiService.getFraudRatioByMedicalRecordTypeChart();
          break;
        case 'getRiskIndicatorsChart':
          const riskData: PrescriptionData = {
            ID: Number(endpointParams.ID),
            jalali_date: endpointParams.jalali_date,
            Adm_date: endpointParams.Adm_date,
            Service: endpointParams.Service,
            provider_name: endpointParams.provider_name,
            provider_specialty: endpointParams.provider_specialty,
            cost_amount: Number(endpointParams.cost_amount),
          };
          result = await apiService.getRiskIndicatorsChart(riskData);
          break;
        case 'getProviderRiskIndicatorChart':
          result = await apiService.getProviderRiskIndicatorChart(
            endpointParams.provider_name,
            endpointParams.indicator
          );
          break;
        case 'getPatientRiskIndicatorChart':
          result = await apiService.getPatientRiskIndicatorChart(
            Number(endpointParams.patient_id),
            endpointParams.indicator
          );
          break;
        default:
          throw new Error('Endpoint not implemented');
      }

      setResults(prev => ({ ...prev, [endpoint.name]: result }));
    } catch (error: any) {
      setErrors(prev => ({ 
        ...prev, 
        [endpoint.name]: error.response?.data?.message || error.message || 'خطای نامشخص'
      }));
    } finally {
      setLoading(false);
    }
  };

  const renderParams = (endpoint: ApiEndpoint) => {
    if (!endpoint.requiresParams || !endpoint.params) return null;

    return (
      <div className="p-4 bg-gray-50 rounded-lg mb-4">
        <h4 className="font-medium text-gray-900 mb-3">پارامترهای مورد نیاز</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {endpoint.params.map((param) => (
            <div key={param.name}>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {param.label} {param.required && <span className="text-red-500">*</span>}
              </label>
              {param.type === 'select' ? (
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  onChange={(e) => handleParamChange(endpoint.name, param.name, e.target.value)}
                  required={param.required}
                >
                  <option value="">انتخاب کنید</option>
                  {param.options?.map((option) => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              ) : (
                <input
                  type={param.type}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder={param.placeholder}
                  onChange={(e) => handleParamChange(endpoint.name, param.name, e.target.value)}
                  required={param.required}
                />
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderResult = (endpointName: string) => {
    const result = results[endpointName];
    const error = errors[endpointName];

    if (loading && selectedEndpoint === endpointName) {
      return (
        <div className="flex items-center justify-center p-4">
          <Loader2 className="h-6 w-6 animate-spin text-primary-500 ml-2" />
          <span>در حال تست...</span>
        </div>
      );
    }

    if (error) {
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <XCircle className="h-5 w-5 text-red-500 ml-2" />
            <span className="text-red-700">{error}</span>
          </div>
        </div>
      );
    }

    if (result) {
      return (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center mb-2">
            <CheckCircle className="h-5 w-5 text-green-500 ml-2" />
            <span className="text-green-700 font-medium">موفق</span>
          </div>
          <pre className="text-sm text-gray-800 overflow-auto max-h-64">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">تست API</h2>
        <p className="text-gray-600">تست تمام endpoint های موجود در سیستم</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* لیست endpoint ها */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Endpoint های موجود</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {endpoints.map((endpoint) => (
              <div
                key={endpoint.name}
                className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                  selectedEndpoint === endpoint.name
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedEndpoint(endpoint.name)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        endpoint.method === 'GET' 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-blue-100 text-blue-700'
                      }`}>
                        {endpoint.method}
                      </span>
                      <span className="text-sm font-mono text-gray-600">{endpoint.path}</span>
                    </div>
                    <h4 className="font-medium text-gray-900">{endpoint.name}</h4>
                    <p className="text-sm text-gray-600 mt-1">{endpoint.description}</p>
                    {endpoint.requiresParams && (
                      <span className="inline-block mt-2 px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-700 rounded">
                        نیاز به پارامتر
                      </span>
                    )}
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      testEndpoint(endpoint);
                    }}
                    disabled={loading}
                    className="btn-primary btn-sm disabled:opacity-50"
                  >
                    <Play className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* نمایش پارامترها و نتایج */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">جزئیات و نتایج</h3>
          <div className="bg-white rounded-lg border border-gray-200 p-4 min-h-96">
            {selectedEndpoint ? (
              <div>
                {renderParams(endpoints.find(e => e.name === selectedEndpoint)!)}
                {renderResult(selectedEndpoint)}
              </div>
            ) : (
              <div className="text-center text-gray-500 h-full flex items-center justify-center">
                <div>
                  <Play className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>برای مشاهده جزئیات، یکی از endpoint ها را انتخاب کنید</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApiTester;
