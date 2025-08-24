"""
Input validation and sanitization for the fraud detection API
اعتبارسنجی و پاکسازی ورودی برای API تشخیص تقلب
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from exceptions import ValidationError

def validate_prescription_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate prescription data for prediction endpoint
    
    Args:
        data: Input prescription data
        
    Returns:
        Validated and sanitized data
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(data, dict):
        raise ValidationError("Input must be a JSON object")
    
    required_fields = ['ID', 'jalali_date', 'Adm_date', 'Service', 'provider_name', 'provider_specialty', 'cost_amount']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    validated_data = {}
    
    # Validate ID
    try:
        validated_data['ID'] = int(data['ID'])
        if validated_data['ID'] <= 0:
            raise ValidationError("ID must be a positive integer", field='ID')
    except (ValueError, TypeError):
        raise ValidationError("ID must be a valid integer", field='ID')
    
    # Validate jalali_date
    validated_data['jalali_date'] = validate_jalali_date(data['jalali_date'])
    
    # Validate Adm_date
    validated_data['Adm_date'] = validate_jalali_date(data['Adm_date'])
    
    # Validate Service
    validated_data['Service'] = validate_string_field(data['Service'], 'Service', max_length=200)
    
    # Validate provider_name
    validated_data['provider_name'] = validate_string_field(data['provider_name'], 'provider_name', max_length=200)
    
    # Validate provider_specialty
    validated_data['provider_specialty'] = validate_string_field(data['provider_specialty'], 'provider_specialty', max_length=200)
    
    # Validate cost_amount
    try:
        validated_data['cost_amount'] = float(data['cost_amount'])
        if validated_data['cost_amount'] < 0:
            raise ValidationError("cost_amount must be non-negative", field='cost_amount')
        if validated_data['cost_amount'] > 1e12:  # 1 trillion
            raise ValidationError("cost_amount is too large", field='cost_amount')
    except (ValueError, TypeError):
        raise ValidationError("cost_amount must be a valid number", field='cost_amount')
    
    return validated_data

def validate_jalali_date(date_str: str) -> str:
    """
    Validate Jalali date format
    
    Args:
        date_str: Date string in YYYY/MM/DD format
        
    Returns:
        Validated date string
        
    Raises:
        ValidationError: If date format is invalid
    """
    if not isinstance(date_str, str):
        raise ValidationError("Date must be a string", field='date')
    
    # Remove any whitespace
    date_str = date_str.strip()
    
    # Check format YYYY/MM/DD
    pattern = r'^\d{4}/\d{1,2}/\d{1,2}$'
    if not re.match(pattern, date_str):
        raise ValidationError("Date must be in YYYY/MM/DD format", field='date')
    
    try:
        year, month, day = map(int, date_str.split('/'))
        
        # Validate year range (1200-1500 for Jalali)
        if year < 1200 or year > 1500:
            raise ValidationError("Year must be between 1200 and 1500", field='date')
        
        # Validate month
        if month < 1 or month > 12:
            raise ValidationError("Month must be between 1 and 12", field='date')
        
        # Validate day
        if day < 1 or day > 31:
            raise ValidationError("Day must be between 1 and 31", field='date')
        
        # Additional validation for specific months
        if month in [1, 2, 3, 4, 5, 6] and day > 31:
            raise ValidationError(f"Day cannot exceed 31 for month {month}", field='date')
        elif month in [7, 8, 9, 10, 11] and day > 30:
            raise ValidationError(f"Day cannot exceed 30 for month {month}", field='date')
        elif month == 12 and day > 29:
            raise ValidationError("Day cannot exceed 29 for month 12", field='date')
        
    except ValueError:
        raise ValidationError("Invalid date components", field='date')
    
    return date_str

def validate_string_field(value: Any, field_name: str, max_length: int = 255, min_length: int = 1) -> str:
    """
    Validate and sanitize string fields
    
    Args:
        value: Field value
        field_name: Name of the field for error messages
        max_length: Maximum allowed length
        min_length: Minimum required length
        
    Returns:
        Sanitized string value
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string", field=field_name)
    
    # Remove leading/trailing whitespace
    value = value.strip()
    
    if len(value) < min_length:
        raise ValidationError(f"{field_name} cannot be empty", field=field_name)
    
    if len(value) > max_length:
        raise ValidationError(f"{field_name} cannot exceed {max_length} characters", field=field_name)
    
    # Basic XSS prevention - remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        if char in value:
            raise ValidationError(f"{field_name} contains invalid characters", field=field_name)
    
    return value

def validate_chart_parameters(params: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
    """
    Validate chart generation parameters
    
    Args:
        params: Chart parameters
        chart_type: Type of chart being generated
        
    Returns:
        Validated parameters
        
    Raises:
        ValidationError: If validation fails
    """
    if chart_type == 'provider_risk_indicator_time_series':
        if 'provider_name' not in params:
            raise ValidationError("provider_name is required for provider risk indicator chart")
        if 'indicator' not in params:
            raise ValidationError("indicator is required for provider risk indicator chart")
        
        params['provider_name'] = validate_string_field(params['provider_name'], 'provider_name')
        params['indicator'] = validate_string_field(params['indicator'], 'indicator')
        
    elif chart_type == 'patient_risk_indicator_time_series':
        if 'patient_id' not in params:
            raise ValidationError("patient_id is required for patient risk indicator chart")
        if 'indicator' not in params:
            raise ValidationError("indicator is required for patient risk indicator chart")
        
        try:
            params['patient_id'] = int(params['patient_id'])
            if params['patient_id'] <= 0:
                raise ValidationError("patient_id must be a positive integer")
        except (ValueError, TypeError):
            raise ValidationError("patient_id must be a valid integer")
        
        params['indicator'] = validate_string_field(params['indicator'], 'indicator')
    
    elif chart_type == 'risk_indicators':
        if 'risk_values' not in params:
            raise ValidationError("risk_values are required for risk indicators chart")
        
        if not isinstance(params['risk_values'], list):
            raise ValidationError("risk_values must be a list")
        
        if len(params['risk_values']) != 11:  # Expected number of risk indicators
            raise ValidationError("risk_values must contain exactly 11 values")
        
        # Validate each risk value
        for i, value in enumerate(params['risk_values']):
            try:
                float_value = float(value)
                if float_value < 0 or float_value > 100:
                    raise ValidationError(f"Risk value {i} must be between 0 and 100")
            except (ValueError, TypeError):
                raise ValidationError(f"Risk value {i} must be a valid number")
    
    return params

def sanitize_input(data: Any) -> Any:
    """
    Basic input sanitization
    
    Args:
        data: Input data to sanitize
        
    Returns:
        Sanitized data
    """
    if isinstance(data, str):
        # Remove potentially dangerous characters
        return data.replace('<', '').replace('>', '').replace('"', '').replace("'", '').replace('&', '')
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    else:
        return data
