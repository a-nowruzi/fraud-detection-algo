import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Union, Tuple

def normalize_features(df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[np.ndarray, StandardScaler]:
    """
    Normalize features using StandardScaler
    
    Args:
        df1: Training dataframe
        df2: New record dataframe
        
    Returns:
        Tuple of (normalized_array, fitted_scaler)
    """
    try:
        # Validate inputs
        if df1.empty or df2.empty:
            raise ValueError("DataFrames cannot be empty")
            
        # Ensure both dataframes have the same columns
        if not set(df1.columns) == set(df2.columns):
            raise ValueError("DataFrames must have the same columns")
        
        # Fit scaler on training data only
        scaler = StandardScaler()
        scaler.fit(df1)
        
        # Transform only the new record
        normalized_array = scaler.transform(df2)
        
        return normalized_array, scaler
        
    except Exception as e:
        print(f"Error in normalization: {str(e)}")
        raise

def normalize_single_record(df: pd.DataFrame, scaler: StandardScaler) -> np.ndarray:
    """
    Normalize a single record using pre-fitted scaler
    
    Args:
        df: Single record dataframe
        scaler: Pre-fitted StandardScaler
        
    Returns:
        Normalized array
    """
    try:
        return scaler.transform(df)
    except Exception as e:
        print(f"Error in single record normalization: {str(e)}")
        raise