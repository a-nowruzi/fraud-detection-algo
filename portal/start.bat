@echo off
echo ========================================
echo راه‌اندازی سیستم تشخیص تقلب پزشکی
echo ========================================
echo.

echo بررسی Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo خطا: Node.js نصب نشده است. لطفاً Node.js را نصب کنید.
    pause
    exit /b 1
)

echo بررسی npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo خطا: npm نصب نشده است.
    pause
    exit /b 1
)

echo نصب وابستگی‌ها...
npm install
if errorlevel 1 (
    echo خطا در نصب وابستگی‌ها
    pause
    exit /b 1
)

echo.
echo ========================================
echo نصب وابستگی‌ها تکمیل شد
echo ========================================
echo.
echo حالا backend را راه‌اندازی کنید:
echo 1. در ترمینال جدید به پوشه api بروید
echo 2. دستور python app.py را اجرا کنید
echo.
echo سپس این فایل را دوباره اجرا کنید تا frontend شروع شود.
echo.
pause

echo راه‌اندازی frontend...
npm run dev
