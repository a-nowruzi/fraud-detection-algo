#!/usr/bin/env python3
"""
Test startup script for fraud detection API (skips database initialization)
اسکریپت راه‌اندازی تست برای API تشخیص تقلب (بدون اتصال به پایگاه داده)
"""

import os
import sys

# Set environment variables for testing
os.environ['SKIP_DB_INIT'] = 'True'
os.environ['CHUNK_SIZE'] = '1000'
os.environ['MAX_CACHE_SIZE'] = '2'
os.environ['MAX_MEMORY_USAGE_MB'] = '1024'

print("=" * 60)
print("Starting Fraud Detection API (TEST MODE)")
print("=" * 60)
print("Database initialization: SKIPPED")
print("Memory optimization: ENABLED")
print("=" * 60)

# Import and start the application
from app import create_app

print("Creating application...")
fraud_app = create_app()

print("Starting Flask server...")
print("The application will start immediately without database connection")
print("Check /health endpoint to verify server is running")
print("Check /memory endpoint to monitor memory usage")
print()

fraud_app.run(host='0.0.0.0', port=5000, debug=False)
