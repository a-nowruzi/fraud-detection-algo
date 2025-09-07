import React, { useState } from 'react';
import { apiService, type PredictionResult, type PrescriptionData } from '../services/api';
import { AlertCircle, CheckCircle, Loader2, BarChart3 } from 'lucide-react';
import RiskIndicators from './RiskIndicators';

const PredictionForm: React.FC = () => {
  const [formData, setFormData] = useState<PrescriptionData>({
    ID: 0,
    jalali_date: '',
    Adm_date: '',
    Service: '',
    provider_name: '',
    provider_specialty: '',
    cost_amount: 0
  });

  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [riskChart, setRiskChart] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'ID' || name === 'cost_amount' ? Number(value) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);
    setRiskChart(null);

    try {
      // Get both prediction and risk indicators chart
      const [predictionResult, riskIndicatorsResult] = await Promise.all([
        apiService.predictFraud(formData),
        apiService.getRiskIndicatorsChart(formData)
      ]);

      setPrediction(predictionResult);
      setRiskChart(riskIndicatorsResult.chart);
    } catch (err) {
      setError('خطا در ارتباط با سرور. لطفاً دوباره تلاش کنید.');
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  const services = [
    'ویزیت متخصص',
    'ویزیت عمومی',
    'دارو و ملزومات دارویی',
    'آزمایش',
    'رادیولوژی',
    'فیزیوتراپی',
    'جراحی',
  ];

  const specialties = [
    'دکترای حرفه‌ای پزشکی',
    'متخصص قلب و عروق',
    'متخصص مغز و اعصاب',
    'متخصص داخلی',
    'متخصص اطفال',
    'متخصص زنان و زایمان',
    'متخصص ارتوپدی',
    'متخصص چشم',
    'متخصص پوست',
  ];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="card">
        <h2 className="text-2xl font-bold mb-6 text-gray-900">اطلاعات نسخه</h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* شماره بیمار */}
            <div>
              <label htmlFor="ID" className="block text-sm font-medium text-gray-700 mb-2">
                شماره بیمار *
              </label>
              <input
                type="number"
                id="ID"
                name="ID"
                value={formData.ID}
                onChange={handleInputChange}
                required
                className="input-field"
                placeholder="مثال: 48928"
              />
            </div>

            {/* تاریخ تولد */}
            <div>
              <label htmlFor="jalali_date" className="block text-sm font-medium text-gray-700 mb-2">
                تاریخ تولد (شمسی) *
              </label>
              <input
                type="text"
                id="jalali_date"
                name="jalali_date"
                value={formData.jalali_date}
                onChange={handleInputChange}
                required
                className="input-field"
                placeholder="مثال: 1361/05/04"
              />
            </div>

            {/* تاریخ پذیرش */}
            <div>
              <label htmlFor="Adm_date" className="block text-sm font-medium text-gray-700 mb-2">
                تاریخ پذیرش (شمسی) *
              </label>
              <input
                type="text"
                id="Adm_date"
                name="Adm_date"
                value={formData.Adm_date}
                onChange={handleInputChange}
                required
                className="input-field"
                placeholder="مثال: 1403/08/05"
              />
            </div>

            {/* نوع خدمت */}
            <div>
              <label htmlFor="Service" className="block text-sm font-medium text-gray-700 mb-2">
                نوع خدمت *
              </label>
              <select
                id="Service"
                name="Service"
                value={formData.Service}
                onChange={handleInputChange}
                required
                className="input-field"
              >
                <option value="">انتخاب کنید</option>
                {services.map(service => (
                  <option key={service} value={service}>{service}</option>
                ))}
              </select>
            </div>

            {/* نام پزشک */}
            <div>
              <label htmlFor="provider_name" className="block text-sm font-medium text-gray-700 mb-2">
                نام پزشک *
              </label>
              <input
                type="text"
                id="provider_name"
                name="provider_name"
                value={formData.provider_name}
                onChange={handleInputChange}
                required
                className="input-field"
                placeholder="مثال: حسینخان خسروخاور"
              />
            </div>

            {/* تخصص پزشک */}
            <div>
              <label htmlFor="provider_specialty" className="block text-sm font-medium text-gray-700 mb-2">
                تخصص پزشک *
              </label>
              <select
                id="provider_specialty"
                name="provider_specialty"
                value={formData.provider_specialty}
                onChange={handleInputChange}
                required
                className="input-field"
              >
                <option value="">انتخاب کنید</option>
                {specialties.map(specialty => (
                  <option key={specialty} value={specialty}>{specialty}</option>
                ))}
              </select>
            </div>

            {/* مبلغ */}
            <div className="md:col-span-2">
              <label htmlFor="cost_amount" className="block text-sm font-medium text-gray-700 mb-2">
                مبلغ (ریال) *
              </label>
              <input
                type="number"
                id="cost_amount"
                name="cost_amount"
                value={formData.cost_amount}
                onChange={handleInputChange}
                required
                className="input-field"
                placeholder="مثال: 2000000"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="ml-2 h-4 w-4 animate-spin" />
                  در حال پردازش...
                </>
              ) : (
                'تشخیص تقلب'
              )}
            </button>
          </div>
        </form>

        {/* نمایش خطا */}
        {error && (
          <div className="mt-6 p-4 bg-danger-50 border border-danger-200 rounded-lg">
            <div className="flex items-center">
              <AlertCircle className="ml-2 h-5 w-5 text-danger-400" />
              <span className="text-danger-700">{error}</span>
            </div>
          </div>
        )}

        {/* نمایش نتیجه */}
        {prediction && (
          <div className="mt-8 space-y-6">
            {/* نتیجه پیش‌بینی */}
            <div className={`p-6 rounded-lg border-2 ${prediction.is_fraud
                ? 'bg-danger-50 border-danger-200'
                : 'bg-success-50 border-success-200'
              }`}>
              <div className="flex items-center mb-4">
                {prediction.is_fraud ? (
                  <AlertCircle className="ml-2 h-6 w-6 text-danger-500" />
                ) : (
                  <CheckCircle className="ml-2 h-6 w-6 text-success-500" />
                )}
                <h3 className={`text-lg font-semibold ${prediction.is_fraud ? 'text-danger-700' : 'text-success-700'
                  }`}>
                  {prediction.is_fraud ? '⚠️ نسخه مشکوک به تقلب' : '✅ نسخه سالم'}
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {prediction.score.toFixed(3)}
                  </div>
                  <div className="text-sm text-gray-600">امتیاز تشخیص</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {prediction.is_fraud ? 'مشکوک' : 'سالم'}
                  </div>
                  <div className="text-sm text-gray-600">وضعیت</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {prediction.prediction === 1 ? '1' : '-1'}
                  </div>
                  <div className="text-sm text-gray-600">کد پیش‌بینی</div>
                </div>
              </div>
            </div>

            {/* نمودار شاخص‌های ریسک */}
            {riskChart && (
              <div className="p-6 bg-white rounded-lg border border-gray-200">
                <div className="flex items-center mb-4">
                  <BarChart3 className="ml-2 h-5 w-5 text-primary-500" />
                  <h3 className="text-lg font-semibold text-gray-900">نمودار شاخص‌های ریسک</h3>
                </div>
                <div className="text-center">
                  <img
                    src={`data:image/png;base64,${riskChart}`}
                    alt="نمودار شاخص‌های ریسک"
                    className="w-full h-auto rounded-lg shadow-sm max-w-2xl mx-auto"
                  />
                </div>
              </div>
            )}

            {/* شاخص‌های ریسک */}
            <div className="p-6 bg-white rounded-lg border border-gray-200">
              <RiskIndicators
                riskScores={prediction.risk_scores}
                features={prediction.features}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictionForm;
