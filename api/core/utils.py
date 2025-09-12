"""
Utility functions for fraud detection API
تابع‌های کمکی برای API تشخیص تقلب
"""

import pandas as pd
import numpy as np
from typing import Union, Dict, Any, List, Optional, Tuple
import logging
from functools import wraps
import time
import psutil
import os
import gc
from config import memory_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_dataframe(df: pd.DataFrame, required_columns: List[str], name: str = "DataFrame") -> bool:
    """
    Validate DataFrame structure and content
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        name: Name for error messages
        
    Returns:
        True if valid, raises ValueError if not
    """
    if df is None:
        raise ValueError(f"{name} cannot be None")
    
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"{name} must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError(f"{name} cannot be empty")
    
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"{name} missing required columns: {missing_cols}")
    
    return True

def safe_division(numerator: Union[float, int], denominator: Union[float, int], 
                  default: float = 0.0) -> float:
    """
    Perform safe division with default value for zero denominator
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division by zero
        
    Returns:
        Division result or default value
    """
    try:
        if denominator == 0 or pd.isna(denominator):
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default

def calculate_percentage_change(current: float, previous: float, 
                              max_change: float = 2000.0) -> float:
    """
    Calculate percentage change with business logic constraints
    
    Args:
        current: Current value
        previous: Previous value
        max_change: Maximum allowed percentage change
        
    Returns:
        Percentage change or 0 if constraints violated
    """
    try:
        if pd.isna(current) or pd.isna(previous) or previous <= 0:
            return 0.0
        
        change = ((current - previous) / previous) * 100
        
        # Apply business logic constraints
        if change < 0 or change > max_change:
            return 0.0
            
        return change
        
    except (TypeError, ValueError):
        return 0.0

def performance_monitor(func):
    """
    Decorator to monitor function performance
    
    Args:
        func: Function to monitor
        
    Returns:
        Wrapped function with performance logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = get_memory_usage_mb()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            end_memory = get_memory_usage_mb()
            memory_diff = end_memory - start_memory
            
            logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds, "
                       f"memory change: {memory_diff:+.2f} MB")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {str(e)}")
            raise
    
    return wrapper

def get_memory_usage_mb() -> float:
    """
    Get current memory usage in MB
    
    Returns:
        Memory usage in MB
    """
    try:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except Exception as e:
        logger.error(f"Error getting memory usage: {str(e)}")
        return 0.0

def check_memory_limit() -> bool:
    """
    Check if memory usage is within limits
    
    Returns:
        True if within limits, False otherwise
    """
    current_memory = get_memory_usage_mb()
    max_memory = memory_config.max_memory_usage_mb
    
    if current_memory > max_memory:
        logger.warning(f"Memory usage ({current_memory:.2f} MB) exceeds limit ({max_memory} MB)")
        return False
    
    return True

def force_memory_cleanup():
    """
    Force memory cleanup by running garbage collection
    """
    try:
        logger.info("Forcing memory cleanup...")
        before_memory = get_memory_usage_mb()
        
        # Run garbage collection multiple times
        for i in range(3):
            gc.collect()
        
        after_memory = get_memory_usage_mb()
        memory_freed = before_memory - after_memory
        
        logger.info(f"Memory cleanup completed. Freed {memory_freed:.2f} MB")
        
    except Exception as e:
        logger.error(f"Error during memory cleanup: {str(e)}")

def memory_monitor(func):
    """
    Decorator to monitor and manage memory usage
    
    Args:
        func: Function to monitor
        
    Returns:
        Wrapped function with memory monitoring
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check memory before execution
        if not check_memory_limit():
            force_memory_cleanup()
        
        start_memory = get_memory_usage_mb()
        
        try:
            result = func(*args, **kwargs)
            
            # Check memory after execution
            end_memory = get_memory_usage_mb()
            memory_used = end_memory - start_memory
            
            logger.info(f"{func.__name__} memory usage: {memory_used:+.2f} MB")
            
            # Force cleanup if memory usage is high
            if end_memory > memory_config.max_memory_usage_mb * 0.8:
                force_memory_cleanup()
            
            return result
            
        except Exception as e:
            logger.error(f"{func.__name__} failed: {str(e)}")
            force_memory_cleanup()
            raise
    
    return wrapper

def clean_numeric_column(series: pd.Series, column_name: str) -> pd.Series:
    """
    Clean numeric column by removing commas and converting to numeric
    
    Args:
        series: Pandas Series to clean
        column_name: Name of the column for logging
        
    Returns:
        Cleaned numeric Series
    """
    try:
        # Remove commas and spaces
        cleaned = series.astype(str).str.replace(',', '').str.strip()
        
        # Convert to numeric
        numeric_series = pd.to_numeric(cleaned, errors='coerce')
        
        # Fill NaN values with 0
        numeric_series = numeric_series.fillna(0).astype(int)
        
        logger.info(f"Cleaned {column_name}: {len(series)} records processed")
        return numeric_series
        
    except Exception as e:
        logger.error(f"Error cleaning {column_name}: {str(e)}")
        raise

def validate_date_range(date_series: pd.Series, min_year: int = 1300, 
                       max_year: int = 1500) -> pd.Series:
    """
    Validate date range for Persian dates
    
    Args:
        date_series: Series of Persian dates
        min_year: Minimum allowed year
        max_year: Maximum allowed year
        
    Returns:
        Boolean Series indicating valid dates
    """
    try:
        # Convert to datetime if needed
        if date_series.dtype == 'object':
            date_series = pd.to_datetime(date_series, errors='coerce')
        
        # Extract year
        years = date_series.dt.year
        
        # Validate range
        valid_dates = (years >= min_year) & (years <= max_year)
        
        invalid_count = (~valid_dates).sum()
        if invalid_count > 0:
            logger.warning(f"Found {invalid_count} dates outside valid range ({min_year}-{max_year})")
        
        return valid_dates
        
    except Exception as e:
        logger.error(f"Error validating date range: {str(e)}")
        raise

@memory_monitor
def memory_usage_optimizer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize DataFrame memory usage by downcasting numeric types
    
    Args:
        df: DataFrame to optimize
        
    Returns:
        DataFrame with optimized memory usage
    """
    try:
        original_memory = df.memory_usage(deep=True).sum()
        
        # Downcast numeric columns
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        # Downcast object columns to category if beneficial
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique values
                df[col] = df[col].astype('category')
        
        final_memory = df.memory_usage(deep=True).sum()
        memory_saved = original_memory - final_memory
        
        logger.info(f"Memory optimization: {memory_saved / 1024**2:.2f} MB saved")
        
        return df
        
    except Exception as e:
        logger.error(f"Error optimizing memory usage: {str(e)}")
        return df

def optimize_dataframe_chunk(df: pd.DataFrame, chunk_name: str = "chunk") -> pd.DataFrame:
    """
    Optimize a DataFrame chunk for memory efficiency
    
    Args:
        df: DataFrame to optimize
        chunk_name: Name for logging
        
    Returns:
        DataFrame with optimized memory usage
    """
    try:
        original_memory = df.memory_usage(deep=True).sum() / 1024**2
        
        # Optimize data types
        df = memory_usage_optimizer(df)
        
        # Remove unnecessary columns if they exist
        unnecessary_cols = ['index', 'level_0', 'level_1']
        for col in unnecessary_cols:
            if col in df.columns:
                df.drop(col, axis=1, inplace=True)
        
        final_memory = df.memory_usage(deep=True).sum() / 1024**2
        memory_saved = original_memory - final_memory
        
        logger.info(f"{chunk_name} optimization: {memory_saved:.2f} MB saved "
                   f"({original_memory:.2f} MB -> {final_memory:.2f} MB)")
        
        return df
        
    except Exception as e:
        logger.error(f"Error optimizing {chunk_name}: {str(e)}")
        return df

def get_system_memory_info() -> Dict[str, Any]:
    """
    Get comprehensive system memory information
    
    Returns:
        Dictionary with memory information
    """
    try:
        # System memory
        system_memory = psutil.virtual_memory()
        
        # Process memory
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info()
        
        return {
            'system': {
                'total_mb': round(system_memory.total / 1024**2, 2),
                'available_mb': round(system_memory.available / 1024**2, 2),
                'used_mb': round(system_memory.used / 1024**2, 2),
                'percent_used': round(system_memory.percent, 2)
            },
            'process': {
                'rss_mb': round(process_memory.rss / 1024**2, 2),
                'vms_mb': round(process_memory.vms / 1024**2, 2),
                'percent': round(process.memory_percent(), 2)
            },
            'limits': {
                'max_memory_mb': memory_config.max_memory_usage_mb,
                'within_limits': check_memory_limit()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system memory info: {str(e)}")
        return {}
