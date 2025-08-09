@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    Fraud Detection API
echo ========================================
echo.
echo Initializing API...
echo.

REM بررسی وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed!
    echo Please install Python from https://python.org.
    pause
    exit /b 1
)

REM بررسی وجود فایل‌های مورد نیاز
if not exist "app.py" (
    echo ❌ Error: app.py file not found!
    pause
    exit /b 1
)

if not exist "DataSEt_FD7.csv" (
    echo ❌ Error: DataSEt_FD7.csv file not found!
    pause
    exit /b 1
)

if not exist "specialties.csv" (
    echo ❌ Error: specialties.csv file not found!
    pause
    exit /b 1
)

echo ✅ All required files are present.
echo.

REM فعال‌سازی محیط مجازی
echo 🔧 Activating virtual environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated.
) else (
    echo ⚠️ Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment created and activated.
)
echo.

REM نصب وابستگی‌ها (در صورت نیاز)
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error: Failed to install dependencies.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully.

echo.
echo 🚀 Starting API...
echo.
echo 📍 API will be available at:
echo    http://localhost:5000
echo.
echo 📋 For documentation (Swagger UI), go to:
echo    http://localhost:5000/docs/
echo.
echo ⏹️ To stop the API, press Ctrl+C.
echo.

REM اجرای API
python app.py

echo.
echo API stopped.
pause
