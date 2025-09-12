@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    Fraud Detection API (Improved)
echo ========================================
echo.
echo Initializing API...
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed!
    echo Please install Python from https://python.org.
    pause
    exit /b 1
)

REM Check for required files
if not exist "main.py" (
    echo ❌ Error: main.py file not found!
    echo Please ensure the improved application is properly set up.
    pause
    exit /b 1
)

REM Check for required directories and files
if not exist "services" (
    echo ❌ Error: services directory not found!
    echo Please ensure all modular components are present.
    pause
    exit /b 1
)

if not exist "routes" (
    echo ❌ Error: routes directory not found!
    echo Please ensure all modular components are present.
    pause
    exit /b 1
)

if not exist "config\config.py" (
    echo ❌ Error: config\config.py file not found!
    echo Please ensure all modular components are present.
    pause
    exit /b 1
)

REM Activate virtual environment
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

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error: Failed to install dependencies.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully.

REM Check database connection
echo 🔍 Checking database connection...
python -c "from config.config import get_db_manager; db = get_db_manager(); print('✅ Database connection successful' if db.test_connection() else '❌ Database connection failed')"
if errorlevel 1 (
    echo ❌ Error: Database connection failed!
    echo Please check your database configuration in config/config.py
    echo Make sure the database server is running and accessible.
    pause
    exit /b 1
)
echo.

REM Check application structure
echo 🔍 Validating application structure...
python -c "import sys; sys.path.append('.'); from main import create_app; print('✅ Application structure is valid')"
if errorlevel 1 (
    echo ❌ Error: Application structure validation failed!
    echo Please check that all modules are properly configured.
    pause
    exit /b 1
)
echo ✅ Application structure validated successfully.
echo.

echo.
echo 🚀 Starting Improved Fraud Detection API...
echo.
echo 📍 API will be available at:
echo    http://localhost:5000
echo.
echo 📋 For documentation (Swagger UI), go to:
echo    http://localhost:5000/docs/
echo.
echo 🔍 Health check endpoint:
echo    http://localhost:5000/health
echo.
echo ✅ Readiness check endpoint:
echo    http://localhost:5000/ready
echo.
echo ⏹️ To stop the API, press Ctrl+C.
echo.

REM Run the improved API
python main.py

echo.
echo API stopped.
pause
