# مستندات فنی API تشخیص تقلب پزشکی

## معماری کلی

### تکنولوژی‌ها
- **Python 3.x** با Flask
- **MySQL** برای پایگاه داده
- **Isolation Forest** برای مدل ML
- **Swagger** برای مستندسازی

### ساختار اصلی
```python
class FraudDetectionApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.prediction_service = None
        self.chart_service = None
        self.data = None
```

## پیکربندی‌ها

### پایگاه داده
```python
@dataclass
class DatabaseConfig:
    host: str = '91.107.174.199'
    database: str = 'testdb'
    user: str = 'testuser'
    password: str = 'testpass123'
    port: int = 3306
```

### مدل ML
```python
@dataclass
class ModelConfig:
    n_estimators: int = 200
    max_samples: int = 36000
    max_features: int = 4
    contamination: float = 0.2
    random_state: int = 42
```

## مسیرهای API

### پیش‌بینی تقلب
**POST /predict**
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

### نمودارها
- `GET /charts/fraud-by-province`
- `GET /charts/fraud-by-gender`
- `GET /charts/fraud-by-age`
- `GET /charts/fraud-ratio-by-age-group`
- `GET /charts/fraud-counts-by-date`

### آمار
- `GET /stats` - آمار کلی سیستم
- `GET /model-info` - اطلاعات مدل

## سرویس‌های اصلی

### PredictionService
```python
class PredictionService:
    def train_model(self, data: pd.DataFrame)
    def predict_new_prescription(self, prescription_data: Dict)
    def is_ready(self) -> bool
```

### FeatureExtractor
**ویژگی‌های استخراج شده**:
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

### ChartService
```python
class ChartService:
    def __init__(self, data: pd.DataFrame = None):
        self.chart_config = {
            'dpi': 300,
            'figsize': (12, 6),
            'style': 'seaborn-v0_8'
        }
```

## مدل یادگیری ماشین

### Isolation Forest
```python
clf = IsolationForest(
    n_estimators=200,
    max_samples=36000,
    max_features=4,
    contamination=0.2,
    random_state=42
)
```

**مزایا**:
- مناسب برای تشخیص تقلب
- عدم نیاز به داده‌های برچسب‌گذاری شده
- سرعت بالا
- مقاوم در برابر نویز

## پایگاه داده

### ساختار جدول
```sql
CREATE TABLE prescriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ID INT NOT NULL,
    jalali_date VARCHAR(10),
    Adm_date VARCHAR(10),
    Service VARCHAR(100),
    provider_name VARCHAR(100),
    provider_specialty VARCHAR(100),
    cost_amount DECIMAL(15,2),
    year_month VARCHAR(7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## امنیت و اعتبارسنجی

### اعتبارسنجی داده‌ها
```python
def validate_prescription_data(data: dict) -> bool:
    required_fields = ['ID', 'jalali_date', 'Adm_date', 'Service', 'provider_name', 'provider_specialty', 'cost_amount']
    
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"فیلد {field} الزامی است")
```

### مدیریت خطاها
```python
class FraudDetectionError(Exception): pass
class ValidationError(FraudDetectionError): pass
class ModelNotReadyError(FraudDetectionError): pass
class DatabaseError(FraudDetectionError): pass
```

### CORS
```python
CORS(self.app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE"]
    }
})
```

## نتیجه‌گیری

API تشخیص تقلب پزشکی شامل:
1. معماری RESTful با Flask
2. مدل Isolation Forest برای تشخیص تقلب
3. 11 ویژگی مختلف برای تحلیل
4. سیستم امنیتی قوی
5. مستندسازی کامل با Swagger
6. قابلیت مقیاس‌پذیری بالا
