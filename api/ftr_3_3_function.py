import pandas as pd
import numpy as np
from typing import Dict, Any, Union

def percent_change_provider_nf(data: pd.DataFrame, new_record: Union[pd.DataFrame, Dict[str, Any]]) -> pd.Series:
    """
    Calculate percentage change in provider costs for fraud detection
    
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
        required_cols = ['Adm_date', 'year_month', 'provider_name', 'cost_amount']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        # Create a copy to avoid modifying original data
        working_data = data.copy()
        
        # Convert dates to datetime if needed
        working_data['Adm_date'] = pd.to_datetime(working_data['Adm_date'], errors='coerce')
        new_record['Adm_date'] = pd.to_datetime(new_record['Adm_date'], errors='coerce')
        
        # Add new record
        working_data = pd.concat([working_data, new_record], ignore_index=True)
        
        # Extract year and month if not already present
        if 'year_month' not in working_data.columns:
            working_data['year_month'] = working_data['Adm_date'].dt.to_period('M')
        
        # Calculate monthly mean amounts for each provider
        monthly_means = working_data.groupby(['year_month', 'provider_name']).agg(
            mean_amount_provider=('cost_amount', 'mean')
        ).reset_index()
        
        # Calculate previous month means (1 and 2 months back)
        monthly_means['previous_mean_amount_provider_1'] = monthly_means.groupby('provider_name')['mean_amount_provider'].shift(1)
        monthly_means['previous_mean_amount_provider_2'] = monthly_means.groupby('provider_name')['mean_amount_provider'].shift(2)
        
        # Calculate average of previous months
        monthly_means['average_previous_mean_provider'] = monthly_means[
            ['previous_mean_amount_provider_1', 'previous_mean_amount_provider_2']
        ].mean(axis=1)
        
        # Calculate percentage change safely
        monthly_means['percent_change_provider'] = np.where(
            (monthly_means['average_previous_mean_provider'] > 0) & 
            (monthly_means['average_previous_mean_provider'].notna()),
            ((monthly_means['mean_amount_provider'] - monthly_means['average_previous_mean_provider']) / 
             monthly_means['average_previous_mean_provider']) * 100,
            0
        )
        
        # Apply business logic constraints
        monthly_means['percent_change_provider'] = monthly_means['percent_change_provider'].apply(
            lambda x: 0 if (pd.isna(x) or x < 0 or x > 2000) else x
        )
        
        # Merge results with main dataframe
        working_data = working_data.merge(
            monthly_means, 
            on=['year_month', 'provider_name'], 
            how='left', 
            suffixes=('', '_monthly')
        )
        
        # Return the last record (new record with calculated features)
        return working_data.iloc[-1]
        
    except Exception as e:
        print(f"Error in percent_change_provider_nf: {str(e)}")
        raise