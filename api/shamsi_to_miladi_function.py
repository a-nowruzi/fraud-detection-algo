import pandas as pd
import numpy as np
import jdatetime
from datetime import datetime
from typing import Union, Optional

def shamsi_to_miladi(date_str: Union[str, pd.Timestamp, None]) -> Optional[datetime]:
    """
    Convert Persian (Shamsi) date to Gregorian (Miladi) date
    
    Args:
        date_str: Persian date in format 'YYYY/MM/DD' or 'YYYY-MM-DD'
        
    Returns:
        Gregorian datetime object, or None if invalid input
    """
    try:
        # Handle None/NaN values
        if pd.isna(date_str) or date_str is None:
            return None
            
        # Convert to string if needed
        if isinstance(date_str, pd.Timestamp):
            date_str = date_str.strftime('%Y/%m/%d')
        elif not isinstance(date_str, str):
            raise TypeError("date_str must be string, Timestamp, or None")
        
        # Clean the date string
        date_str = date_str.strip().replace('-', '/')
        
        # Validate date format
        if not date_str.count('/') == 2:
            raise ValueError("Date must be in format 'YYYY/MM/DD' or 'YYYY-MM-DD'")
        
        # Split and convert to integers
        try:
            year, month, day = map(int, date_str.split('/'))
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
            gregorian_date = jdatetime.datetime(year, month, day).togregorian()
            return gregorian_date
        except Exception as e:
            raise ValueError(f"Invalid Persian date: {str(e)}")
        
    except Exception as e:
        print(f"Error converting Persian date {date_str}: {str(e)}")
        return None

def shamsi_to_miladi_batch(dates: pd.Series) -> pd.Series:
    """
    Convert a series of Persian dates to Gregorian dates
    
    Args:
        dates: Series of Persian dates
        
    Returns:
        Series of Gregorian datetime objects
    """
    try:
        return dates.apply(shamsi_to_miladi)
    except Exception as e:
        print(f"Error in batch date conversion: {str(e)}")
        return pd.Series([None] * len(dates))

def miladi_to_shamsi(date_obj: Union[datetime, pd.Timestamp, None]) -> Optional[str]:
    """
    Convert Gregorian (Miladi) date to Persian (Shamsi) date
    
    Args:
        date_obj: Gregorian datetime object
        
    Returns:
        Persian date string in format 'YYYY/MM/DD', or None if invalid input
    """
    try:
        # Handle None/NaN values
        if pd.isna(date_obj) or date_obj is None:
            return None
            
        # Convert to datetime if needed
        if isinstance(date_obj, pd.Timestamp):
            date_obj = date_obj.to_pydatetime()
        elif not isinstance(date_obj, datetime):
            raise TypeError("date_obj must be datetime, Timestamp, or None")
        
        # Convert to Persian date
        try:
            persian_date = jdatetime.datetime.fromgregorian(
                datetime=date_obj
            )
            return persian_date.strftime('%Y/%m/%d')
        except Exception as e:
            raise ValueError(f"Error converting to Persian date: {str(e)}")
        
    except Exception as e:
        print(f"Error converting Gregorian date {date_obj}: {str(e)}")
        return None
