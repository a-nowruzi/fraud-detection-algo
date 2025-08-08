#!/bin/bash

echo "========================================"
echo "راه‌اندازی سیستم تشخیص تقلب پزشکی"
echo "========================================"
echo

echo "بررسی Node.js..."
if ! command -v node &> /dev/null; then
    echo "خطا: Node.js نصب نشده است. لطفاً Node.js را نصب کنید."
    exit 1
fi

echo "بررسی npm..."
if ! command -v npm &> /dev/null; then
    echo "خطا: npm نصب نشده است."
    exit 1
fi

echo "نصب وابستگی‌ها..."
npm install
if [ $? -ne 0 ]; then
    echo "خطا در نصب وابستگی‌ها"
    exit 1
fi

echo
echo "========================================"
echo "نصب وابستگی‌ها تکمیل شد"
echo "========================================"
echo
echo "حالا backend را راه‌اندازی کنید:"
echo "1. در ترمینال جدید به پوشه api بروید"
echo "2. دستور python app.py را اجرا کنید"
echo
echo "سپس این فایل را دوباره اجرا کنید تا frontend شروع شود."
echo
read -p "برای ادامه Enter را فشار دهید..."

echo "راه‌اندازی frontend..."
npm run dev
