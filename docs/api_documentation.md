# مستندات فنی API تشخیص تقلب پزشکی

## فهرست مطالب
1. [معماری کلی API](#معماری-کلی-api)
2. [پیکربندی‌ها](#پیکربندی‌ها)
3. [مسیرهای API](#مسیرهای-api)
4. [سرویس‌های اصلی](#سرویس‌های-اصلی)
5. [مدل یادگیری ماشین](#مدل-یادگیری-ماشین)
6. [استخراج ویژگی‌ها](#استخراج-ویژگی‌ها)
7. [پایگاه داده](#پایگاه-داده)
8. [امنیت و اعتبارسنجی](#امنیت-و-اعتبارسنجی)

---

## معماری کلی API

### تکنولوژی‌های استفاده شده
- **زبان برنامه‌نویسی**: Python 3.x
- **فریم‌ورک**: Flask
- **معماری**: RESTful API با Blueprint Pattern
- **پایگاه داده**: MySQL
- **مدل ML**: Isolation Forest
- **مستندسازی**: Swagger/Flasgger

### ساختار کلی
```python
class FraudDetectionApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.prediction_service = None
        self.chart_service = None
        self.data = None
        
        self._configure_app()
        self._register_blueprints()
        self._register_error_handlers()
```

---

## پیکربندی‌ها

### 1. پیکربندی پایگاه داده
```python
@dataclass
class DatabaseConfig:
    host: str = '91.107.174.199'
    database: str = 'testdb'
    user: str = 'testuser'
    password: str = 'testpass123'
    port: int = 3306
    charset: str = 'utf8mb4'
    autocommit: bool = True
```

### 2. پیکربندی مدل
```python
@dataclass
class ModelConfig:
    n_estimators: int = 200        # تعداد درختان
    max_samples: int = 36000       # حداکثر نمونه‌ها
    max_features: int = 4          # حداکثر ویژگی‌ها
    contamination: float = 0.2     # نرخ آلودگی (تخمین تقلب)
    random_state: int = 42         # حالت تصادفی
```

### 3. پیکربندی اپلیکیشن
```python
@dataclass
class AppConfig:
    debug: bool = False
    host: str = '0.0.0.0'
    port: int = 5000
    secret_key: str = 'your-secret-key-here'
    chart_dpi: int = 300
    chart_figsize: tuple = (12, 6)
    max_percentage_change: float = 2000.0
```

---

## مسیرهای API

### 1. مسیرهای پیش‌بینی

#### پیش‌بینی تقلب برای نسخه جدید
**Endpoint**: `POST /predict`

**پارامترهای ورودی**:
```json
{
  "ID": 48928,
  "jalali_date": "1361/05/04",
  "Adm_date": "1403/08/05",
  "Service": "ویزیت متخصص",
  "provider_name": "حسینخان خسروخاور",
  "provider_specialty": "دکترای حرفه‌ای پزشکی",
  "cost_amount": 2000000
}
```

**پاسخ**:
```json
{
  "prediction": -1,
  "score": 0.85,
  "is_fraud": true,
  "risk_scores": [0.7, 0.8, 0.9],
  "features": {
    "unq_ratio_provider": 1.2,
    "unq_ratio_patient": 1.1,
    "percent_change_provider": 15.5,
    "percent_change_patient": 12.3,
    "percent_difference": 8.7,
    "percent_diff_ser": 5.2,
    "percent_diff_spe": 3.8,
    "percent_diff_spe2": 2.1,
    "percent_diff_ser_patient": 4.6,
    "percent_diff_serv": 6.9,
    "Ratio": 1.15
  }
}
```

### 2. مسیرهای نمودار

#### نمودارهای اصلی
- `GET /charts/fraud-by-province` - نمودار تقلب بر اساس استان
- `GET /charts/fraud-by-gender` - نمودار تقلب بر اساس جنسیت
- `GET /charts/fraud-by-age` - نمودار تقلب بر اساس سن

#### نمودارهای نسبت تقلب
- `GET /charts/fraud-ratio-by-age-group` - نسبت تقلب بر اساس گروه سنی
- `GET /charts/province-fraud-ratio` - نسبت تقلب بر اساس استان
- `GET /charts/province-gender-fraud-percentage` - درصد تقلب بر اساس استان و جنسیت

#### نمودارهای زمانی
- `GET /charts/fraud-counts-by-date` - تعداد تقلب بر اساس تاریخ
- `GET /charts/fraud-ratio-by-date` - نسبت تقلب بر اساس تاریخ

#### نمودارهای بیمه و اداری
- `GET /charts/fraud-ratio-by-ins-cover` - نسبت تقلب بر اساس پوشش بیمه
- `GET /charts/fraud-ratio-by-invoice-type` - نسبت تقلب بر اساس نوع فاکتور
- `GET /charts/fraud-ratio-by-medical-record-type` - نسبت تقلب بر اساس نوع پرونده پزشکی

#### نمودارهای شاخص ریسک
- `POST /charts/risk-indicators` - نمودار شاخص‌های ریسک برای نسخه خاص
- `GET /charts/provider-risk-indicator` - نمودار شاخص ریسک ارائه‌دهنده
- `GET /charts/patient-risk-indicator` - نمودار شاخص ریسک بیمار

### 3. مسیرهای آمار

#### آمار کلی سیستم
**Endpoint**: `GET /stats`

**پاسخ**:
```json
{
  "total_prescriptions": 100000,
  "fraud_prescriptions": 20000,
  "normal_prescriptions": 80000,
  "fraud_percentage": 20.0,
  "model_contamination": 0.2,
  "features_count": 11
}
```

#### اطلاعات مدل
**Endpoint**: `GET /model-info`

**پاسخ**:
```json
{
  "status": "ready",
  "model_type": "IsolationForest",
  "training_samples": 50000,
  "feature_count": 11,
  "max_features": 4,
  "max_samples": 36000,
  "n_estimators": 200,
  "contamination": 0.2
}
```

---

## سرویس‌های اصلی

### 1. سرویس پیش‌بینی (PredictionService)

#### کلاس اصلی
```python
class PredictionService:
    def __init__(self, data: pd.DataFrame = None, clf: IsolationForest = None, scaler: StandardScaler = None):
        self.data = data
        self.clf = clf
        self.scaler = scaler
        self.data_final = None
```

#### متدهای اصلی
- `train_model(data)`: آموزش مدل Isolation Forest
- `predict_new_prescription(prescription_data)`: پیش‌بینی تقلب برای نسخه جدید
- `is_ready()`: بررسی آماده بودن مدل
- `get_prediction_stats()`: دریافت آمار پیش‌بینی‌ها

### 2. سرویس نمودار (ChartService)

#### کلاس اصلی
```python
class ChartService:
    def __init__(self, data: pd.DataFrame = None):
        self.data = data
        self.chart_config = {
            'dpi': 300,
            'figsize': (12, 6),
            'style': 'seaborn-v0_8'
        }
```

#### نوع نمودارها
- نمودارهای میله‌ای (Bar Charts)
- نمودارهای دایره‌ای (Pie Charts)
- نمودارهای خطی (Line Charts)
- نمودارهای پراکندگی (Scatter Plots)
- نمودارهای هیستوگرام (Histograms)

### 3. سرویس استخراج ویژگی‌ها (FeatureExtractor)

#### ویژگی‌های استخراج شده
```python
feature_columns = [
    'unq_ratio_provider',      # نسبت کل ارائه‌دهندگان به منحصر به فرد
    'unq_ratio_patient',       # نسبت کل بیماران به منحصر به فرد
    'percent_change_provider', # درصد تغییر هزینه ارائه‌دهنده
    'percent_change_patient',  # درصد تغییر هزینه بیمار
    'percent_difference',      # درصد تفاوت
    'percent_diff_ser',        # درصد تفاوت خدمات
    'percent_diff_spe',        # درصد تفاوت تخصص
    'percent_diff_spe2',       # درصد تفاوت تخصص 2
    'percent_diff_ser_patient', # درصد تفاوت خدمات بیمار
    'percent_diff_serv',       # درصد تفاوت خدمات
    'Ratio'                    # نسبت کلی
]
```

---

## مدل یادگیری ماشین

### Isolation Forest

#### پارامترهای مدل
```python
clf = IsolationForest(
    n_estimators=200,        # تعداد درختان
    max_samples=36000,       # حداکثر نمونه‌ها
    max_features=4,          # حداکثر ویژگی‌ها
    contamination=0.2,       # نرخ آلودگی (تخمین تقلب)
    random_state=42          # حالت تصادفی
)
```

#### مزایای Isolation Forest
- مناسب برای تشخیص تقلب
- نیاز به داده‌های برچسب‌گذاری شده ندارد
- سرعت بالا در آموزش و پیش‌بینی
- مقاوم در برابر نویز
- قابلیت تشخیص الگوهای غیرعادی

### پیش‌پردازش داده‌ها

#### 1. استانداردسازی
```python
scaler = StandardScaler()
X = scaler.fit_transform(self.data_final)
```

#### 2. مدیریت مقادیر گمشده
```python
self.data_final.dropna(inplace=True)
```

#### 3. تبدیل تاریخ‌ها
- تبدیل تاریخ شمسی به میلادی
- محاسبه سن بیمار
- استخراج ویژگی‌های زمانی

---

## استخراج ویژگی‌ها

### ویژگی‌های ارائه‌دهنده

#### 1. نسبت ارائه‌دهندگان
```python
def _extract_provider_features(self):
    providers_count_per_month = self.data.groupby(['year_month', 'ID']).agg(
        total_providers_monthly=('provider_name', 'count')
    ).reset_index()
    
    unique_providers_per_month = self.data.groupby(['year_month', 'ID']).agg(
        unique_providers=('provider_name', 'nunique')
    ).reset_index()
    
    self.data['unq_ratio_provider'] = self.data.apply(
        lambda row: safe_division(row['total_providers_monthly'], row['unique_providers']), 
        axis=1
    )
```

#### 2. تغییرات هزینه ارائه‌دهنده
```python
def _extract_cost_change_features(self):
    monthly_means = self.data.groupby(['year_month', 'provider_name']).agg(
        mean_amount_provider=('cost_amount', 'mean')
    ).reset_index()
    
    monthly_means['previous_mean_amount_provider_1'] = monthly_means.groupby('provider_name')['mean_amount_provider'].shift(1)
    monthly_means['previous_mean_amount_provider_2'] = monthly_means.groupby('provider_name')['mean_amount_provider'].shift(2)
```

### ویژگی‌های بیمار

#### 1. نسبت بیماران
```python
def _extract_patient_features(self):
    patients_count_per_month = self.data.groupby(['year_month', 'provider_name']).agg(
        total_patients_monthly=('ID', 'count')
    ).reset_index()
    
    unique_patients_per_month = self.data.groupby(['year_month', 'provider_name']).agg(
        unique_patients=('ID', 'nunique')
    ).reset_index()
    
    self.data['unq_ratio_patient'] = self.data.apply(
        lambda row: safe_division(row['total_patients_monthly'], row['unique_patients']), 
        axis=1
    )
```

### ویژگی‌های خدمات

#### 1. تغییرات خدمات
```python
def _extract_service_features(self):
    service_means = self.data.groupby(['year_month', 'Service']).agg(
        mean_amount_service=('cost_amount', 'mean')
    ).reset_index()
    
    service_means['previous_mean_amount_service_1'] = service_means.groupby('Service')['mean_amount_service'].shift(1)
    service_means['previous_mean_amount_service_2'] = service_means.groupby('Service')['mean_amount_service'].shift(2)
```

### ویژگی‌های تخصص

#### 1. تغییرات تخصص
```python
def _extract_specialty_features(self):
    specialty_means = self.data.groupby(['year_month', 'provider_specialty']).agg(
        mean_amount_specialty=('cost_amount', 'mean')
    ).reset_index()
    
    specialty_means['previous_mean_amount_specialty_1'] = specialty_means.groupby('provider_specialty')['mean_amount_specialty'].shift(1)
    specialty_means['previous_mean_amount_specialty_2'] = specialty_means.groupby('provider_specialty')['mean_amount_specialty'].shift(2)
```

---

## پایگاه داده

### ساختار جداول

#### جدول اصلی نسخه‌ها
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

### مدیریت اتصال

#### کلاس مدیریت پایگاه داده
```python
class DatabaseManager:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = None
    
    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.config.host,
            database=self.config.database,
            user=self.config.user,
            password=self.config.password,
            port=self.config.port,
            charset=self.config.charset,
            autocommit=self.config.autocommit
        )
    
    def execute_query(self, query: str, params: tuple = None):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def close(self):
        if self.connection:
            self.connection.close()
```

---

## امنیت و اعتبارسنجی

### اعتبارسنجی داده‌های ورودی

#### کلاس اعتبارسنجی
```python
def validate_prescription_data(data: dict) -> bool:
    required_fields = ['ID', 'jalali_date', 'Adm_date', 'Service', 'provider_name', 'provider_specialty', 'cost_amount']
    
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"فیلد {field} الزامی است")
    
    if not isinstance(data['ID'], int) or data['ID'] <= 0:
        raise ValidationError("شماره بیمار باید عدد مثبت باشد")
    
    if not isinstance(data['cost_amount'], (int, float)) or data['cost_amount'] < 0:
        raise ValidationError("مبلغ هزینه باید عدد مثبت باشد")
    
    return True
```

### پاکسازی داده‌ها

#### تابع پاکسازی
```python
def sanitize_input(data: str) -> str:
    # حذف کاراکترهای خطرناک
    dangerous_chars = ['<', '>', '"', "'", '&', ';']
    for char in dangerous_chars:
        data = data.replace(char, '')
    
    # حذف فضاهای اضافی
    data = data.strip()
    
    return data
```

### مدیریت خطاها

#### کلاس‌های خطا
```python
class FraudDetectionError(Exception):
    """خطای پایه سیستم تشخیص تقلب"""
    pass

class ValidationError(FraudDetectionError):
    """خطای اعتبارسنجی داده‌ها"""
    pass

class ModelNotReadyError(FraudDetectionError):
    """خطای عدم آماده بودن مدل"""
    pass

class DatabaseError(FraudDetectionError):
    """خطای پایگاه داده"""
    pass
```

### CORS و امنیت

#### پیکربندی CORS
```python
CORS(self.app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

## نتیجه‌گیری

API تشخیص تقلب پزشکی یک سیستم قدرتمند و پیشرفته است که شامل:

1. **معماری RESTful**: با Blueprint Pattern برای سازماندهی بهتر کد
2. **مدل هوشمند**: بر اساس Isolation Forest برای تشخیص تقلب
3. **استخراج ویژگی‌های پیشرفته**: با 11 ویژگی مختلف
4. **امنیت بالا**: با اعتبارسنجی و پاکسازی داده‌ها
5. **مستندسازی کامل**: با Swagger برای API
6. **قابلیت مقیاس‌پذیری**: برای استفاده در محیط‌های تولیدی

این API قابلیت‌های پیشرفته‌ای برای تشخیص تقلب در نسخه‌های پزشکی فراهم می‌کند و می‌تواند به عنوان یک ابزار قدرتمند در حوزه سلامت مورد استفاده قرار گیرد.
