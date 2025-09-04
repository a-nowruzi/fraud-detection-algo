"""
Main Entry Point for Fraud Detection API

This file serves as the main entry point for the API and handles
proper imports from the organized directory structure.
"""

import sys
import os

# Add the current directory to Python path so we can import from subdirectories
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main application
from core.app import create_app, MemoryOptimizedFraudDetectionApp

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Memory-Optimized Fraud Detection API")
    print("=" * 60)
    
    # Create and run the application
    fraud_app = create_app()
    fraud_app.run()
else:
    # For WSGI servers like Gunicorn
    fraud_app = create_app()
    app = fraud_app.app
