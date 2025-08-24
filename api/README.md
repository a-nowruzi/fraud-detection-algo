# API تشخیص تقلب پزشکی

این پوشه شامل تمام فایل‌های backend برای API تشخیص تقلب پزشکی است.

## ساختار فایل‌ها

- `app.py` - فایل اصلی API Flask
- `requirements.txt` - وابستگی‌های Python
- `run_api.bat` - اسکریپت اجرا برای Windows
- `run_api.sh` - اسکریپت اجرا برای Linux/Mac
- `test_api.py` - تست‌های API
- `database_config.py` - تنظیمات پایگاه داده MariaDB
- `setup_database.py` - اسکریپت راه‌اندازی پایگاه داده
- `DATABASE_SETUP.md` - راهنمای کامل راه‌اندازی پایگاه داده
- فایل‌های تابع مختلف (ftr_*.py, *_function.py)

## پایگاه داده

این سیستم از MariaDB به عنوان منبع داده استفاده می‌کند:

- **سرور**: 91.107.174.199
- **پایگاه داده**: testdb
- **کاربر**: testuser
- **رمز عبور**: testpass123

## راه‌اندازی اولیه

### 1. نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### 2. راه‌اندازی پایگاه داده
```bash
# راه‌اندازی کامل با import خودکار CSV
python setup_database.py setup

# یا راه‌اندازی دستی
python setup_database.py create_tables
python setup_database.py import DataSEt_FD7.csv fraud_data
python setup_database.py import specialties.csv specialties
```

### 3. تست اتصال پایگاه داده
```bash
python -c "from database_config import get_db_manager; db = get_db_manager(); print('موفق' if db.test_connection() else 'ناموفق')"
```

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
- سرور MariaDB باید در دسترس باشد
- برای اطلاعات بیشتر به `DATABASE_SETUP.md` مراجعه کنید

## مهاجرت از CSV

اگر فایل‌های CSV دارید، می‌توانید آن‌ها را به پایگاه داده منتقل کنید:

```bash
python setup_database.py setup
```

این دستور جداول را ایجاد کرده و داده‌های CSV را import می‌کند.
