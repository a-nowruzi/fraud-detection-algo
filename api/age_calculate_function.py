import pandas as pd
import numpy as np
import jdatetime
from datetime import datetime
from typing import Union, Optional

def calculate_age(sh_date: Union[str, pd.Timestamp, None]) -> Optional[int]:
    """
    Calculate age from Persian (Shamsi) date
    
    Args:
        sh_date: Persian date in format 'YYYY/MM/DD' or 'YYYY-MM-DD'
        
    Returns:
        Age in years, or None if invalid input
    """
    try:
        # Handle None/NaN values
        if pd.isna(sh_date) or sh_date is None:
            return None
            
        # Convert to string if needed
        if isinstance(sh_date, pd.Timestamp):
            sh_date = sh_date.strftime('%Y/%m/%d')
        elif not isinstance(sh_date, str):
            raise TypeError("sh_date must be string, Timestamp, or None")
        
        # Clean the date string
        sh_date = sh_date.strip().replace('-', '/')
        
        # Validate date format
        if not sh_date.count('/') == 2:
            raise ValueError("Date must be in format 'YYYY/MM/DD' or 'YYYY-MM-DD'")
        
        # Split and convert to integers
        try:
            year, month, day = map(int, sh_date.split('/'))
        except ValueError:
            raise ValueError("Date components must be valid integers")
        
        # Validate date ranges
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        if not (1 <= day <= 31):
            raise ValueError("Day must be between 1 and 31")
        if year < 1300 or year > 1500:  # Reasonable Persian year range
            raise ValueError("Year must be between 1300 and 1500")
        
        # Convert Persian date to Gregorian
        try:
            jalali_date = jdatetime.date(year, month, day).togregorian()
        except Exception as e:
            raise ValueError(f"Invalid Persian date: {str(e)}")
        
        # Get current date
        today = datetime.now()
        
        # Calculate age
        age = today.year - jalali_date.year
        
        # Adjust age if birthday hasn't occurred this year
        if (today.month, today.day) < (jalali_date.month, jalali_date.day):
            age -= 1
        
        # Validate calculated age
        if age < 0 or age > 150:
            raise ValueError(f"Calculated age {age} is outside reasonable range")
        
        return age
        
    except Exception as e:
        print(f"Error calculating age from {sh_date}: {str(e)}")
        return None

def calculate_age_batch(dates: pd.Series) -> pd.Series:
    """
    Calculate ages for a series of Persian dates
    
    Args:
        dates: Series of Persian dates
        
    Returns:
        Series of calculated ages
    """
    try:
        return dates.apply(calculate_age)
    except Exception as e:
        print(f"Error in batch age calculation: {str(e)}")
        return pd.Series([None] * len(dates))
