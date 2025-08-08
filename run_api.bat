@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    API تشخیص تقلب پزشکی
echo ========================================
echo.
echo در حال راه‌اندازی API...
echo.

REM بررسی وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ خطا: Python نصب نشده است!
    echo لطفاً Python را از https://python.org نصب کنید.
    pause
    exit /b 1
)

REM بررسی وجود فایل‌های مورد نیاز
if not exist "app.py" (
    echo ❌ خطا: فایل app.py یافت نشد!
    pause
    exit /b 1
)

if not exist "DataSEt_FD7.CSV" (
    echo ❌ خطا: فایل DataSEt_FD7.CSV یافت نشد!
    pause
    exit /b 1
)

if not exist "specialties.csv" (
    echo ❌ خطا: فایل specialties.csv یافت نشد!
    pause
    exit /b 1
)

echo ✅ فایل‌های مورد نیاز موجود هستند.
echo.

REM نصب وابستگی‌ها (در صورت نیاز)
@REM echo 📦 بررسی وابستگی‌ها...
@REM pip install -r requirements.txt >nul 2>&1
@REM if errorlevel 1 (
@REM     echo ⚠️ هشدار: برخی وابستگی‌ها نصب نشدند.
@REM     echo لطفاً دستی نصب کنید: pip install -r requirements.txt
@REM     echo.
@REM )

echo.
echo 🚀 شروع API...
echo.
echo 📍 API در آدرس زیر در دسترس خواهد بود:
echo    http://localhost:5000
echo.
echo 📋 برای مشاهده مستندات (Swagger UI) به آدرس زیر بروید:
echo    http://localhost:5000/docs/
echo.
echo ⏹️ برای توقف API، Ctrl+C را فشار دهید.
echo.

REM اجرای API
python app.py

echo.
echo API متوقف شد.
pause
