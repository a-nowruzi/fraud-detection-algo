#!/usr/bin/env python3
"""
Production startup script for fraud detection API
اسکریپت راه‌اندازی تولید برای API تشخیص تقلب
"""

import os
import sys

# Set environment variables for production
os.environ['SKIP_DB_INIT'] = 'False'
os.environ['CHUNK_SIZE'] = '5000'
os.environ['MAX_CACHE_SIZE'] = '5'
os.environ['MAX_MEMORY_USAGE_MB'] = '2048'
os.environ['ENABLE_STREAMING'] = 'True'
os.environ['ENABLE_ASYNC_INIT'] = 'True'

print("=" * 60)
print("Starting Fraud Detection API (PRODUCTION MODE)")
print("=" * 60)
print("Database initialization: ENABLED")
print("Memory optimization: ENABLED")
print("Async initialization: ENABLED")
print("=" * 60)

# Import and start the application
from app import create_app

print("Creating application...")
fraud_app = create_app()

print("Starting Flask server...")
print("The application will start immediately and initialize services asynchronously")
print("Check /ready endpoint to monitor initialization progress")
print("Check /memory endpoint to monitor memory usage")
print()

fraud_app.run(host='0.0.0.0', port=5000, debug=False)
