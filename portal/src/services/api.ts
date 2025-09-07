import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';
// const API_BASE_URL = 'https://fraudapi.nowruzi.top';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface PrescriptionData {
  ID: number;
  jalali_date: string;
  Adm_date: string;
  Service: string;
  provider_name: string;
  provider_specialty: string;
  cost_amount: number;
}

export interface PredictionResult {
  prediction: number;
  score: number;
  is_fraud: boolean;
  risk_scores: number[];
  features: Record<string, number>;
}

export interface SystemStats {
  total_prescriptions: number;
  fraud_prescriptions: number;
  normal_prescriptions: number;
  fraud_percentage: number;
  model_contamination: number;
  features_count: number;
}

export interface ModelInfo {
  status: 'ready' | 'not_ready';
  model_type: string;
  training_samples: number;
  feature_count: number;
  max_features: number;
  max_samples: number;
  n_estimators: number;
  contamination: number;
}

export interface ChartResponse {
  chart: string;
}

export interface RiskIndicatorsResponse {
  chart: string;
  prediction: PredictionResult;
}

export const apiService = {
  // پیش‌بینی تقلب برای نسخه جدید
  predictFraud: async (data: PrescriptionData): Promise<PredictionResult> => {
    const response = await api.post('/predict', data);
    return response.data;
  },

  // دریافت آمار کلی سیستم
  getStats: async (): Promise<SystemStats> => {
    const response = await api.get('/stats');
    return response.data;
  },

  // دریافت اطلاعات مدل
  getModelInfo: async (): Promise<ModelInfo> => {
    const response = await api.get('/model-info');
    return response.data;
  },

  // نمودارهای اصلی
  getFraudByProvinceChart: async (): Promise<ChartResponse> => {
    const response = await api.get('/charts/fraud-by-province');
    return response.data;
  },

  getFraudByGenderChart: async (): Promise<ChartResponse> => {
    const response = await api.get('/charts/fraud-by-gender');
    return response.data;
  },

  getFraudByAgeChart: async (): Promise<ChartResponse> => {
    const response = await api.get('/charts/fraud-by-age');
    return response.data;
  },

  // نمودارهای نسبت تقلب
  getFraudRatioByAgeGroupChart: async (): Promise<ChartResponse> => {
    const response = await api.get('/charts/fraud-ratio-by-age-group');
    return response.data;
  },

  getProvinceFraudRatioChart: async (): Promise<ChartResponse> => {
    const response = await api.get('/charts/province-fraud-ratio');
    return response.data;
  },

  getProvinceGenderFraudPercentageChart: async (): Promise<ChartResponse> => {
    const response = await api.get('/charts/province-gender-fraud-percentage');
    return response.data;
  },

  // نمودارهای زمانی
  getFraudCountsByDateChart: async (): Promise<ChartResponse> => {
    const response = await api.get('/charts/fraud-counts-by-date');
    return response.data;
  },

  getFraudRatioByDateChart: async (): Promise<ChartResponse> => {
    const response = await api.get('/charts/fraud-ratio-by-date');
    return response.data;
  },

  // نمودارهای بیمه و اداری
  getFraudRatioByInsCoverChart: async (): Promise<ChartResponse> => {
    const response = await api.get('/charts/fraud-ratio-by-ins-cover');
    return response.data;
  },

  getFraudRatioByInvoiceTypeChart: async (): Promise<ChartResponse> => {
    const response = await api.get('/charts/fraud-ratio-by-invoice-type');
    return response.data;
  },

  getFraudRatioByMedicalRecordTypeChart: async (): Promise<ChartResponse> => {
    const response = await api.get('/charts/fraud-ratio-by-medical-record-type');
    return response.data;
  },

  // نمودارهای شاخص ریسک
  getRiskIndicatorsChart: async (data: PrescriptionData): Promise<RiskIndicatorsResponse> => {
    const response = await api.post('/charts/risk-indicators', data);
    return response.data;
  },

  getProviderRiskIndicatorChart: async (providerName: string, indicator: string): Promise<ChartResponse> => {
    const response = await api.get('/charts/provider-risk-indicator', {
      params: { provider_name: providerName, indicator }
    });
    return response.data;
  },

  getPatientRiskIndicatorChart: async (patientId: number, indicator: string): Promise<ChartResponse> => {
    const response = await api.get('/charts/patient-risk-indicator', {
      params: { patient_id: patientId, indicator }
    });
    return response.data;
  },
};
