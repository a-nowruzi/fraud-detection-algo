# API تشخیص تقلب پزشکی

این پوشه شامل تمام فایل‌های backend برای API تشخیص تقلب پزشکی است.

## ساختار فایل‌ها

- `app.py` - فایل اصلی API Flask
- `requirements.txt` - وابستگی‌های Python
- `run_api.bat` - اسکریپت اجرا برای Windows
- `run_api.sh` - اسکریپت اجرا برای Linux/Mac
- `test_api.py` - تست‌های API
- `API_README.md` - مستندات کامل API
- `DataSEt_FD7.csv` - مجموعه داده اصلی
- `specialties.csv` - فایل تخصص‌های پزشکی
- فایل‌های تابع مختلف (ftr_*.py, *_function.py)

## نحوه اجرا

### Windows
```bash
cd api
run_api.bat
```

### Linux/Mac
```bash
cd api
chmod +x run_api.sh
./run_api.sh
```

### دستی
```bash
cd api
pip install -r requirements.txt
python app.py
```

## دسترسی به API

- API اصلی: http://localhost:5000
- مستندات Swagger: http://localhost:5000/docs/

## نکات مهم

- اطمینان حاصل کنید که Python 3.7+ نصب شده است
- تمام وابستگی‌ها در requirements.txt تعریف شده‌اند
- فایل‌های داده (CSV) باید در همین پوشه قرار داشته باشند
