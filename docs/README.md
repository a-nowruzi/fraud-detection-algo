# مستندات فنی سیستم تشخیص تقلب پزشکی

## فهرست مطالب
- [معماری کلی](#معماری-کلی)
- [API Backend](#api-backend)
- [Portal Frontend](#portal-frontend)
- [مدل یادگیری ماشین](#مدل-یادگیری-ماشین)
- [پایگاه داده](#پایگاه-داده)
- [امنیت](#امنیت)

## معماری کلی

سیستم تشخیص تقلب پزشکی از دو بخش اصلی تشکیل شده است:

### Backend (API)
- **زبان**: Python 3.x
- **فریم‌ورک**: Flask
- **پایگاه داده**: MySQL
- **مدل ML**: Isolation Forest

### Frontend (Portal)
- **زبان**: TypeScript
- **فریم‌ورک**: React 19
- **Build Tool**: Vite
- **UI**: Tailwind CSS + Recharts

## API Backend

### ساختار اصلی
```python
class FraudDetectionApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.prediction_service = None
        self.chart_service = None
        self.data = None
```

### مسیرهای اصلی
- `POST /predict` - پیش‌بینی تقلب
- `GET /charts/*` - نمودارهای مختلف
- `GET /stats` - آمار سیستم
- `GET /model-info` - اطلاعات مدل

### سرویس‌های اصلی
1. **PredictionService**: مدیریت پیش‌بینی‌ها
2. **ChartService**: تولید نمودارها
3. **FeatureExtractor**: استخراج ویژگی‌ها

### ویژگی‌های استخراج شده (11 ویژگی)
- `unq_ratio_provider` - نسبت ارائه‌دهندگان
- `unq_ratio_patient` - نسبت بیماران
- `percent_change_provider` - تغییرات هزینه ارائه‌دهنده
- `percent_change_patient` - تغییرات هزینه بیمار
- `percent_difference` - درصد تفاوت
- `percent_diff_ser` - تفاوت خدمات
- `percent_diff_spe` - تفاوت تخصص
- `percent_diff_spe2` - تفاوت تخصص 2
- `percent_diff_ser_patient` - تفاوت خدمات بیمار
- `percent_diff_serv` - تفاوت خدمات
- `Ratio` - نسبت کلی

## Portal Frontend

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

### کامپوننت‌های اصلی
1. **PredictionForm**: فرم پیش‌بینی تقلب
2. **ChartsGallery**: گالری نمودارها
3. **RiskIndicators**: شاخص‌های ریسک
4. **Layout**: قالب کلی

### صفحات اصلی
1. **Dashboard**: داشبورد اصلی
2. **PredictPage**: صفحه پیش‌بینی
3. **ChartsPage**: صفحه نمودارها
4. **StatsPage**: صفحه آمار
5. **ApiTestPage**: صفحه تست API

## مدل یادگیری ماشین

### Isolation Forest
```python
clf = IsolationForest(
    n_estimators=200,        # تعداد درختان
    max_samples=36000,       # حداکثر نمونه‌ها
    max_features=4,          # حداکثر ویژگی‌ها
    contamination=0.2,       # نرخ آلودگی
    random_state=42          # حالت تصادفی
)
```

### مزایا
- مناسب برای تشخیص تقلب
- عدم نیاز به داده‌های برچسب‌گذاری شده
- سرعت بالا
- مقاوم در برابر نویز

## پایگاه داده

### ساختار جدول اصلی
```sql
CREATE TABLE prescriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ID INT NOT NULL,                    -- شماره بیمار
    jalali_date VARCHAR(10),            -- تاریخ تولد شمسی
    Adm_date VARCHAR(10),               -- تاریخ پذیرش شمسی
    Service VARCHAR(100),               -- نوع خدمت
    provider_name VARCHAR(100),         -- نام ارائه‌دهنده
    provider_specialty VARCHAR(100),    -- تخصص ارائه‌دهنده
    cost_amount DECIMAL(15,2),          -- مبلغ هزینه
    year_month VARCHAR(7),              -- سال و ماه
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## امنیت

### اعتبارسنجی داده‌ها
- بررسی فیلدهای الزامی
- اعتبارسنجی نوع داده‌ها
- محدودیت‌های عددی

### پاکسازی داده‌ها
- حذف کاراکترهای خطرناک
- پاکسازی فضاهای اضافی

### CORS
```python
CORS(self.app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE"]
    }
})
```

## ویژگی‌های کلیدی

1. **پیش‌بینی تقلب**: تشخیص تقلب در نسخه‌های پزشکی
2. **نمودارهای تحلیلی**: 15+ نوع نمودار مختلف
3. **شاخص‌های ریسک**: محاسبه و نمایش ریسک
4. **آمار کامل**: گزارش‌گیری جامع
5. **رابط کاربری مدرن**: طراحی واکنش‌گرا
6. **API کامل**: مستندسازی با Swagger
7. **امنیت بالا**: اعتبارسنجی و پاکسازی
8. **مقیاس‌پذیری**: قابلیت توسعه

## فایل‌های مستندات

- `api_tech_doc.md` - مستندات کامل API
- `portal_tech_doc.md` - مستندات کامل Portal
- `complete_technical_documentation.md` - مستندات جامع سیستم

## نتیجه‌گیری

سیستم تشخیص تقلب پزشکی یک راه‌حل جامع و پیشرفته است که شامل:

1. **معماری RESTful** با Flask
2. **رابط کاربری مدرن** با React 19
3. **مدل هوشمند** Isolation Forest
4. **11 ویژگی مختلف** برای تحلیل
5. **سیستم امنیتی قوی**
6. **مستندات کامل**
7. **قابلیت مقیاس‌پذیری بالا**

این سیستم می‌تواند به عنوان یک ابزار قدرتمند برای تشخیص تقلب در حوزه پزشکی مورد استفاده قرار گیرد.
