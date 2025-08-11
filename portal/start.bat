@echo off
echo.
echo ========================================
echo    Fraud Detection System Frontend
echo ========================================
echo.
echo Initializing Frontend...
echo.

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Node.js is not installed. Please install Node.js.
    pause
    exit /b 1
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: npm is not installed.
    pause
    exit /b 1
)

echo ✅ All required files are present.
echo.

echo 📦 Installing dependencies...
npm install
if errorlevel 1 (
    echo ❌ Error in installing dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully.

echo 🚀 Starting frontend...
npm run dev
