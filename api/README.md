# Fraud Detection API - Organized Structure

This document describes the organized structure of the Fraud Detection API folder.

## 📁 Directory Structure

```
api/
├── core/                           # Core application files
│   ├── app.py                     # Main Flask application
│   ├── database_config.py         # Database configuration and management
│   ├── exceptions.py              # Custom exception classes
│   ├── utils.py                   # Utility functions and helpers
│   └── validators.py              # Input validation functions
│
├── config/                         # Configuration files
│   ├── config.py                  # Main configuration settings
│   └── env_example.txt            # Environment variables template
│
├── functions/                      # Feature extraction functions
│   ├── __init__.py                # Package initialization
│   ├── age_calculate_function.py  # Age calculation utilities
│   ├── add_one_month_function.py  # Date manipulation functions
│   ├── shamsi_to_miladi_function.py # Persian to Gregorian date conversion
│   ├── normalazation_function.py  # Data normalization functions
│   ├── ftr_1_function.py         # Feature 1 extraction
│   ├── ftr_2_function.py         # Feature 2 extraction
│   ├── ftr_3_3_function.py       # Feature 3.3 extraction
│   ├── ftr_4_function.py         # Feature 4 extraction
│   ├── ftr_5_function.py         # Feature 5 extraction
│   ├── ftr_6_function.py         # Feature 6 extraction
│   ├── ftr_7_function.py         # Feature 7 extraction
│   ├── ftr_7_2_function.py       # Feature 7.2 extraction
│   ├── ftr_8_1_function.py       # Feature 8.1 extraction
│   ├── ftr_8_2_function.py       # Feature 8.2 extraction
│   └── ftr_9_function.py         # Feature 9 extraction
│
├── services/                       # Business logic services
│   ├── __init__.py
│   ├── prediction_service.py      # Fraud prediction service
│   ├── chart_service.py           # Chart generation service
│   └── feature_extractor.py       # Feature extraction service
│
├── routes/                         # API route definitions
│   ├── __init__.py
│   ├── prediction_routes.py       # Prediction endpoints
│   └── chart_routes.py            # Chart endpoints
│
├── models/                         # ML models and metadata
│   ├── fraud_detection_model.pkl  # Trained fraud detection model
│   ├── fraud_detection_scaler.pkl # Data scaler
│   └── model_metadata.pkl         # Model metadata
│
├── scripts/                        # Utility scripts
│   ├── run_api.bat                # Windows batch file to run API
│   ├── run_improved.py            # Improved runner script
│   └── setup_database.py          # Database setup script
│
├── logs/                           # Log files
│   └── fraud_detection_optimized.log
│
├── notebooks/                      # Jupyter notebooks
│   └── Project_FD 0.ipynb         # Project notebook
│
├── assets/                         # Static assets (fonts, etc.)
├── venv/                          # Python virtual environment
├── requirements.txt                # Python dependencies
└── README.md                      # This file
```

## 🔧 Key Components

### Core (`core/`)
Contains the main application logic, database configuration, and essential utilities.

### Functions (`functions/`)
All feature extraction functions organized in one place. Each function handles a specific aspect of data processing.

### Services (`services/`)
Business logic layer that orchestrates the application functionality.

### Routes (`routes/`)
API endpoint definitions organized by functionality.

### Configuration (`config/`)
Centralized configuration management.

### Scripts (`scripts/`)
Utility scripts for running and managing the application.

## 🚀 Getting Started

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the API:**
   ```bash
   # Windows
   scripts/run_api.bat
   
   # Or directly (recommended)
   python main.py
   
   # Or from core directory
   python core/app.py
   ```

3. **Access the API:**
   - Main API: `http://localhost:5000`
   - Documentation: `http://localhost:5000/docs/`
   - Health Check: `http://localhost:5000/health`

## 📊 Features

- **Fraud Detection**: ML-based fraud detection using Isolation Forest
- **Feature Extraction**: 11 different risk indicators
- **Memory Optimization**: Streaming data processing for large datasets
- **Gunicorn Compatible**: Production-ready deployment
- **Swagger Documentation**: Interactive API documentation
- **Persian Date Support**: Jalali calendar integration

## 🔍 API Endpoints

- `POST /predict` - Fraud prediction for new prescriptions
- `GET /charts/*` - Various analytical charts
- `GET /stats` - System statistics
- `GET /health` - Health check
- `GET /memory` - Memory usage status

## 🧹 Maintenance

- **Logs**: Check `logs/` directory for application logs
- **Cache**: Use `/cache/clear` endpoint to clear data cache
- **Memory**: Monitor memory usage via `/memory` endpoint

## 📝 Notes

- The API is optimized for memory usage with streaming data processing
- All feature functions are now centralized in the `functions/` directory
- Configuration is centralized in the `config/` directory
- Scripts are organized in the `scripts/` directory for easy access
