"""
Custom exceptions for the fraud detection API
استثناهای سفارشی برای API تشخیص تقلب
"""

from typing import Optional, Dict, Any
from flask import jsonify

class FraudDetectionError(Exception):
    """Base exception for fraud detection API"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class ValidationError(FraudDetectionError):
    """Raised when input validation fails"""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)
        self.field = field

class DataNotFoundError(FraudDetectionError):
    """Raised when required data is not found"""
    def __init__(self, message: str, resource: Optional[str] = None):
        super().__init__(message, status_code=404)
        self.resource = resource

class DatabaseError(FraudDetectionError):
    """Raised when database operations fail"""
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(message, status_code=503)
        self.operation = operation

class ModelNotReadyError(FraudDetectionError):
    """Raised when the ML model is not ready"""
    def __init__(self, message: str = "Model is not ready for predictions"):
        super().__init__(message, status_code=503)

class ChartGenerationError(FraudDetectionError):
    """Raised when chart generation fails"""
    def __init__(self, message: str, chart_type: Optional[str] = None):
        super().__init__(message, status_code=500)
        self.chart_type = chart_type

def handle_exception(error: Exception):
    """Global exception handler"""
    if isinstance(error, FraudDetectionError):
        response = {
            'error': error.message,
            'status_code': error.status_code,
            'details': error.details
        }
        return jsonify(response), error.status_code
    
    # Handle unexpected errors
    response = {
        'error': 'Internal server error',
        'status_code': 500,
        'details': {'message': str(error)} if str(error) else {}
    }
    return jsonify(response), 500
