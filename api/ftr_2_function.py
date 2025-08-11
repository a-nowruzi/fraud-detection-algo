import pandas as pd
import numpy as np
from typing import Dict, Any, Union

def unique_patients_nf(data: pd.DataFrame, new_record: Union[pd.DataFrame, Dict[str, Any]]) -> pd.Series:
    """
    Calculate unique patients ratio for fraud detection
    
    Args:
        data: Historical data DataFrame
        new_record: New record to analyze (DataFrame or dict)
        
    Returns:
        Series containing the calculated features for the new record
    """
    try:
        # Input validation
        if data.empty:
            raise ValueError("Historical data cannot be empty")
            
        if isinstance(new_record, dict):
            new_record = pd.DataFrame([new_record])
        elif not isinstance(new_record, pd.DataFrame):
            raise TypeError("new_record must be DataFrame or dict")
            
        # Ensure required columns exist
        required_cols = ['year_month', 'provider_name', 'ID']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        # Create a copy to avoid modifying original data
        working_data = data.copy()
        
        # Add new record
        working_data = pd.concat([working_data, new_record], ignore_index=True)
        
        # Calculate total patients per month for each provider
        patients_count_per_month = working_data.groupby(['year_month', 'provider_name']).agg(
            total_patients_monthly=('ID', 'count')
        ).reset_index()
        
        # Calculate unique patients per month for each provider
        unique_patients_per_month = working_data.groupby(['year_month', 'provider_name']).agg(
            unique_patients=('ID', 'nunique')
        ).reset_index()
        
        # Merge results efficiently
        working_data = working_data.merge(
            patients_count_per_month, 
            on=['year_month', 'provider_name'], 
            how='left'
        )
        
        working_data = working_data.merge(
            unique_patients_per_month, 
            on=['year_month', 'provider_name'], 
            how='left'
        )
        
        # Calculate ratio safely (avoid division by zero)
        working_data['unq_ratio_patient'] = np.where(
            working_data['unique_patients'] > 0,
            working_data['total_patients_monthly'] / working_data['unique_patients'],
            0
        )
        
        # Return the last record (new record with calculated features)
        return working_data.iloc[-1]
        
    except Exception as e:
        print(f"Error in unique_patients_nf: {str(e)}")
        raise