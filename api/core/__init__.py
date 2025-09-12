"""
Core Package for Fraud Detection API

This package contains the core application files including the main Flask app,
database configuration, exceptions, utilities, and validators.
"""

# Import core components
from .app import create_app, FraudDetectionApp
from .database_config import get_db_manager
from .exceptions import FraudDetectionError, handle_exception
from .utils import clean_numeric_column, memory_usage_optimizer
from .validators import validate_prescription_data, sanitize_input

__all__ = [
    'create_app',
    'FraudDetectionApp',
    'get_db_manager',
    'FraudDetectionError',
    'handle_exception',
    'clean_numeric_column',
    'memory_usage_optimizer',
    'validate_prescription_data',
    'sanitize_input'
]

__version__ = '1.0.0'
__author__ = 'Fraud Detection Team'
__description__ = 'Core functionality for medical fraud detection API'
