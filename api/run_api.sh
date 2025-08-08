#!/bin/bash

echo ""
echo "========================================"
echo "    API تشخیص تقلب پزشکی"
echo "========================================"
echo ""
echo "در حال راه‌اندازی API..."
echo ""

# بررسی وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ خطا: Python3 نصب نشده است!"
    echo "لطفاً Python3 را نصب کنید."
    exit 1
fi

# بررسی وجود فایل‌های مورد نیاز
if [ ! -f "app.py" ]; then
    echo "❌ خطا: فایل app.py یافت نشد!"
    exit 1
fi

if [ ! -f "DataSEt_FD7.csv" ]; then
    echo "❌ خطا: فایل DataSEt_FD7.csv یافت نشد!"
    exit 1
fi

if [ ! -f "specialties.csv" ]; then
    echo "❌ خطا: فایل specialties.csv یافت نشد!"
    exit 1
fi

echo "✅ فایل‌های مورد نیاز موجود هستند."
echo ""

# نصب وابستگی‌ها (در صورت نیاز)
echo "📦 بررسی وابستگی‌ها..."
pip3 install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️ هشدار: برخی وابستگی‌ها نصب نشدند."
    echo "لطفاً دستی نصب کنید: pip3 install -r requirements.txt"
    echo ""
fi

echo ""
echo "🚀 شروع API..."
echo ""
echo "📍 API در آدرس زیر در دسترس خواهد بود:"
echo "   http://localhost:5000"
echo ""
echo "📋 برای مشاهده مستندات (Swagger UI) به آدرس زیر بروید:"
echo "   http://localhost:5000/docs/"
echo ""
echo "⏹️ برای توقف API، Ctrl+C را فشار دهید."
echo ""

# اجرای API
python3 app.py

echo ""
echo "API متوقف شد."
