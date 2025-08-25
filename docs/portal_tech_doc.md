# مستندات فنی Portal تشخیص تقلب پزشکی

## معماری کلی

### تکنولوژی‌ها
- **TypeScript** با React 19
- **Vite** برای Build Tool
- **React Router DOM** برای Routing
- **Axios** برای HTTP Client
- **Recharts** برای نمودارها
- **Lucide React** برای آیکون‌ها

### ساختار اصلی
```typescript
function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/predict" element={<PredictPage />} />
          <Route path="/charts" element={<ChartsPage />} />
          <Route path="/stats" element={<StatsPage />} />
          <Route path="/api-test" element={<ApiTestPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}
```

## پیکربندی‌ها

### package.json
```json
{
  "name": "portal",
  "version": "0.0.0",
  "type": "module",
  "dependencies": {
    "react": "^19.1.1",
    "react-dom": "^19.1.1",
    "axios": "^1.6.0",
    "react-router-dom": "^6.20.0",
    "recharts": "^2.8.0",
    "lucide-react": "^0.294.0",
    "clsx": "^2.0.0"
  }
}
```

### Vite Config
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

## سرویس API

### رابط‌های TypeScript
```typescript
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
```

### متدهای سرویس API
```typescript
export const apiService = {
  // پیش‌بینی تقلب
  predictFraud: async (data: PrescriptionData): Promise<PredictionResult>,
  
  // آمار و اطلاعات
  getStats: async (): Promise<SystemStats>,
  getModelInfo: async (): Promise<ModelInfo>,
  
  // نمودارهای اصلی
  getFraudByProvinceChart: async (): Promise<ChartResponse>,
  getFraudByGenderChart: async (): Promise<ChartResponse>,
  getFraudByAgeChart: async (): Promise<ChartResponse>,
  
  // نمودارهای نسبت تقلب
  getFraudRatioByAgeGroupChart: async (): Promise<ChartResponse>,
  getProvinceFraudRatioChart: async (): Promise<ChartResponse>,
  getProvinceGenderFraudPercentageChart: async (): Promise<ChartResponse>,
  
  // نمودارهای زمانی
  getFraudCountsByDateChart: async (): Promise<ChartResponse>,
  getFraudRatioByDateChart: async (): Promise<ChartResponse>,
  
  // نمودارهای بیمه و اداری
  getFraudRatioByInsCoverChart: async (): Promise<ChartResponse>,
  getFraudRatioByInvoiceTypeChart: async (): Promise<ChartResponse>,
  getFraudRatioByMedicalRecordTypeChart: async (): Promise<ChartResponse>,
  
  // نمودارهای شاخص ریسک
  getRiskIndicatorsChart: async (data: PrescriptionData): Promise<RiskIndicatorsResponse>,
  getProviderRiskIndicatorChart: async (providerName: string, indicator: string): Promise<ChartResponse>,
  getPatientRiskIndicatorChart: async (patientId: number, indicator: string): Promise<ChartResponse>,
};
```

## کامپوننت‌های اصلی

### 1. فرم پیش‌بینی (PredictionForm.tsx)

#### State Management
```typescript
const [formData, setFormData] = useState<PrescriptionData>({
  ID: 0,
  jalali_date: '',
  Adm_date: '',
  Service: '',
  provider_name: '',
  provider_specialty: '',
  cost_amount: 0,
});

const [prediction, setPrediction] = useState<PredictionResult | null>(null);
const [riskChart, setRiskChart] = useState<string | null>(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
```

#### متدهای اصلی
```typescript
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
  
  try {
    const [predictionResult, riskIndicatorsResult] = await Promise.all([
      apiService.predictFraud(formData),
      apiService.getRiskIndicatorsChart(formData)
    ]);
    
    setPrediction(predictionResult);
    setRiskChart(riskIndicatorsResult.chart);
  } catch (err) {
    setError('خطا در ارتباط با سرور. لطفاً دوباره تلاش کنید.');
  } finally {
    setLoading(false);
  }
};
```

#### فیلدهای فرم
- **شماره بیمار**: ورودی عددی
- **تاریخ تولد**: ورودی تاریخ شمسی
- **تاریخ پذیرش**: ورودی تاریخ شمسی
- **نوع خدمت**: انتخاب از لیست
- **نام ارائه‌دهنده**: ورودی متنی
- **تخصص ارائه‌دهنده**: انتخاب از لیست
- **مبلغ هزینه**: ورودی عددی

### 2. گالری نمودارها (ChartsGallery.tsx)

#### نوع نمودارها
- **نمودارهای آماری کلی**: نمایش آمار عمومی سیستم
- **نمودارهای توزیع تقلب**: بر اساس استان، جنسیت، سن
- **نمودارهای زمانی**: روند تقلب در طول زمان
- **نمودارهای مقایسه‌ای**: مقایسه شاخص‌های مختلف

#### کامپوننت‌های نمودار
```typescript
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { PieChart, Pie, Cell } from 'recharts';
import { LineChart, Line } from 'recharts';
```

### 3. شاخص‌های ریسک (RiskIndicators.tsx)

#### ویژگی‌های نمایش
- **امتیاز ریسک کلی**: نمایش عددی و رنگی
- **شاخص‌های مختلف ریسک**: نمودارهای جداگانه
- **نمودارهای مقایسه‌ای**: مقایسه با میانگین
- **توصیه‌های امنیتی**: بر اساس امتیاز ریسک

### 4. Layout (Layout.tsx)

#### ساختار کلی
```typescript
const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        {/* Navigation Menu */}
      </nav>
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
};
```

## صفحات اصلی

### 1. داشبورد (Dashboard.tsx)

#### محتوای صفحه
- **آمار کلی سیستم**: تعداد کل نسخه‌ها، درصد تقلب
- **نمودارهای خلاصه**: نمودارهای مهم در یک نگاه
- **وضعیت مدل**: آماده یا غیرآماده بودن مدل
- **پیوندهای سریع**: دسترسی سریع به بخش‌های مختلف

### 2. صفحه پیش‌بینی (PredictPage.tsx)

#### محتوای صفحه
- **فرم ورود اطلاعات**: برای وارد کردن داده‌های نسخه
- **نمایش نتایج**: نتیجه پیش‌بینی و امتیاز ریسک
- **نمودارهای تحلیلی**: نمودارهای مربوط به نسخه وارد شده

### 3. صفحه نمودارها (ChartsPage.tsx)

#### محتوای صفحه
- **گالری کامل نمودارها**: تمام نمودارهای موجود
- **فیلترهای مختلف**: فیلتر بر اساس نوع، تاریخ، منطقه
- **امکان دانلود نمودارها**: ذخیره نمودارها به صورت تصویر

### 4. صفحه آمار (StatsPage.tsx)

#### محتوای صفحه
- **آمار تفصیلی سیستم**: آمار کامل و جزئیات
- **اطلاعات مدل**: پارامترها و عملکرد مدل
- **عملکرد سیستم**: آمار عملکرد و کارایی

### 5. صفحه تست API (ApiTestPage.tsx)

#### محتوای صفحه
- **تست مستقیم API**: ارسال درخواست‌های تست
- **نمایش پاسخ‌ها**: نمایش کامل پاسخ‌های API
- **دیباگ کردن**: ابزارهای دیباگ و عیب‌یابی

## استایل‌ها و UI

### CSS Framework
- **Tailwind CSS**: برای استایل‌دهی
- **Responsive Design**: طراحی واکنش‌گرا
- **Dark/Light Mode**: پشتیبانی از حالت‌های مختلف

### کامپوننت‌های UI
```typescript
// Card Component
const Card: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
    {children}
  </div>
);

// Button Component
const Button: React.FC<{ children: React.ReactNode; onClick?: () => void; variant?: 'primary' | 'secondary' }> = ({ 
  children, 
  onClick, 
  variant = 'primary' 
}) => (
  <button 
    onClick={onClick}
    className={`px-4 py-2 rounded-md font-medium ${
      variant === 'primary' 
        ? 'bg-blue-600 text-white hover:bg-blue-700' 
        : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
    }`}
  >
    {children}
  </button>
);
```

## مدیریت State

### Local State
- **useState**: برای state محلی کامپوننت‌ها
- **useEffect**: برای side effects
- **useCallback**: برای بهینه‌سازی عملکرد

### Global State
- **Context API**: برای state سراسری (در صورت نیاز)
- **Local Storage**: برای ذخیره تنظیمات کاربر

## Error Handling

### مدیریت خطاها
```typescript
const handleError = (error: any) => {
  if (error.response) {
    // خطای سرور
    setError(`خطای سرور: ${error.response.status}`);
  } else if (error.request) {
    // خطای شبکه
    setError('خطا در ارتباط با سرور');
  } else {
    // خطای دیگر
    setError('خطای غیرمنتظره');
  }
};
```

### Loading States
```typescript
const [loading, setLoading] = useState(false);

const handleAsyncOperation = async () => {
  setLoading(true);
  try {
    await someAsyncOperation();
  } catch (error) {
    handleError(error);
  } finally {
    setLoading(false);
  }
};
```

## Performance Optimization

### بهینه‌سازی‌ها
- **React.memo**: برای جلوگیری از re-render غیرضروری
- **useMemo**: برای محاسبات سنگین
- **useCallback**: برای توابع
- **Lazy Loading**: برای کامپوننت‌های بزرگ
- **Code Splitting**: تقسیم کد به chunks

### Lazy Loading
```typescript
const ChartsPage = lazy(() => import('./pages/ChartsPage'));
const StatsPage = lazy(() => import('./pages/StatsPage'));

// در App.tsx
<Suspense fallback={<div>در حال بارگذاری...</div>}>
  <ChartsPage />
</Suspense>
```

## نتیجه‌گیری

Portal تشخیص تقلب پزشکی شامل:

1. **معماری مدرن**: React 19 با TypeScript
2. **رابط کاربری پیشرفته**: با Tailwind CSS و Recharts
3. **سرویس API کامل**: برای ارتباط با Backend
4. **کامپوننت‌های قابل استفاده مجدد**: برای توسعه آسان
5. **مدیریت State بهینه**: با React Hooks
6. **Error Handling قوی**: برای تجربه کاربری بهتر
7. **Performance Optimization**: برای عملکرد بهینه
8. **Responsive Design**: سازگار با تمام دستگاه‌ها

این Portal یک رابط کاربری کامل و کاربرپسند برای سیستم تشخیص تقلب پزشکی فراهم می‌کند.
