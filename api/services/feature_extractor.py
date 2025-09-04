"""
Memory-optimized feature extraction service for fraud detection
سرویس استخراج ویژگی‌های بهینه‌سازی شده حافظه برای تشخیص تقلب
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from core.utils import safe_division, calculate_percentage_change, performance_monitor
from config.config import app_config
import logging
import gc

logger = logging.getLogger(__name__)

class MemoryOptimizedFeatureExtractor:
    """Memory-optimized service for extracting features from prescription data"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.feature_columns = [
            'unq_ratio_provider', 'unq_ratio_patient', 'percent_change_provider',
            'percent_change_patient', 'percent_difference', 'percent_diff_ser',
            'percent_diff_spe', 'percent_diff_spe2', 'percent_diff_ser_patient',
            'percent_diff_serv', 'Ratio'
        ]
    
    @performance_monitor
    def extract_all_features(self) -> pd.DataFrame:
        """Extract all features from the dataset with memory optimization"""
        try:
            logger.info("Starting memory-optimized feature extraction...")
            
            # Extract features using helper methods with memory optimization
            self._extract_provider_features_efficiently()
            self._extract_patient_features_efficiently()
            self._extract_service_features_efficiently()
            self._extract_specialty_features_efficiently()
            self._extract_ratio_features_efficiently()
            
            # Clean up memory after feature extraction
            gc.collect()
            
            logger.info("Memory-optimized feature extraction completed successfully")
            return self.data
            
        except Exception as e:
            logger.error(f"Error in feature extraction: {str(e)}")
            raise
    
    def _extract_provider_features_efficiently(self):
        """Extract provider-related features with memory optimization"""
        logger.info("Extracting provider features efficiently...")
        
        # Feature 1: Ratio of total providers to unique providers
        # Use more efficient groupby operations
        provider_stats = self.data.groupby(['year_month', 'ID']).agg({
            'provider_name': ['count', 'nunique']
        }).reset_index()
        
        # Flatten column names
        provider_stats.columns = ['year_month', 'ID', 'total_providers_monthly', 'unique_providers']
        
        # Merge efficiently
        self.data = self.data.merge(provider_stats, on=['year_month', 'ID'], how='left')
        
        # Calculate ratio efficiently
        self.data['unq_ratio_provider'] = self.data.apply(
            lambda row: safe_division(row['total_providers_monthly'], row['unique_providers']), 
            axis=1
        )
        
        # Clean up temporary data
        del provider_stats
        gc.collect()
    
    def _extract_patient_features_efficiently(self):
        """Extract patient-related features with memory optimization"""
        logger.info("Extracting patient features efficiently...")
        
        # Feature 2: Ratio of total patients to unique patients
        patient_stats = self.data.groupby(['year_month', 'provider_name']).agg({
            'ID': ['count', 'nunique']
        }).reset_index()
        
        # Flatten column names
        patient_stats.columns = ['year_month', 'provider_name', 'total_patients_monthly', 'unique_patients']
        
        # Merge efficiently
        self.data = self.data.merge(patient_stats, on=['year_month', 'provider_name'], how='left')
        
        # Calculate ratio efficiently
        self.data['unq_ratio_patient'] = self.data.apply(
            lambda row: safe_division(row['total_patients_monthly'], row['unique_patients']), 
            axis=1
        )
        
        # Clean up temporary data
        del patient_stats
        gc.collect()
        
        # Feature 3 & 4: Provider and Patient cost change percentage
        self._extract_cost_change_features_efficiently()
    
    def _extract_cost_change_features_efficiently(self):
        """Extract cost change percentage features with memory optimization"""
        logger.info("Extracting cost change features efficiently...")
        
        # Provider cost change - use more efficient approach
        provider_monthly = self.data.groupby(['year_month', 'provider_name'])['cost_amount'].mean().reset_index()
        provider_monthly.columns = ['year_month', 'provider_name', 'mean_amount_provider']
        
        # Calculate previous values efficiently
        provider_monthly['previous_mean_amount_provider_1'] = provider_monthly.groupby('provider_name')['mean_amount_provider'].shift(1)
        provider_monthly['previous_mean_amount_provider_2'] = provider_monthly.groupby('provider_name')['mean_amount_provider'].shift(2)
        provider_monthly['average_previous_mean_provider'] = provider_monthly[['previous_mean_amount_provider_1', 'previous_mean_amount_provider_2']].mean(axis=1)
        
        # Calculate percentage change efficiently
        provider_monthly['percent_change_provider'] = provider_monthly.apply(
            lambda row: calculate_percentage_change(
                row['mean_amount_provider'], 
                row['average_previous_mean_provider'],
                app_config.max_percentage_change
            ), 
            axis=1
        )
        
        # Merge only necessary columns
        provider_merge_cols = ['year_month', 'provider_name', 'percent_change_provider']
        self.data = self.data.merge(provider_monthly[provider_merge_cols], on=['year_month', 'provider_name'], how='left')
        
        # Patient cost change - similar efficient approach
        patient_monthly = self.data.groupby(['year_month', 'ID'])['cost_amount'].mean().reset_index()
        patient_monthly.columns = ['year_month', 'ID', 'mean_amount_patient']
        
        patient_monthly['previous_mean_amount_patient_1'] = patient_monthly.groupby('ID')['mean_amount_patient'].shift(1)
        patient_monthly['previous_mean_amount_patient_2'] = patient_monthly.groupby('ID')['mean_amount_patient'].shift(2)
        patient_monthly['average_previous_mean_patient'] = patient_monthly[['previous_mean_amount_patient_1', 'previous_mean_amount_patient_2']].mean(axis=1)
        
        patient_monthly['percent_change_patient'] = patient_monthly.apply(
            lambda row: calculate_percentage_change(
                row['mean_amount_patient'], 
                row['average_previous_mean_patient'],
                app_config.max_percentage_change
            ), 
            axis=1
        )
        
        # Merge only necessary columns
        patient_merge_cols = ['year_month', 'ID', 'percent_change_patient']
        self.data = self.data.merge(patient_monthly[patient_merge_cols], on=['year_month', 'ID'], how='left')
        
        # Clean up temporary data
        del provider_monthly, patient_monthly
        gc.collect()
    
    def _extract_service_features_efficiently(self):
        """Extract service-related features with memory optimization"""
        logger.info("Extracting service features efficiently...")
        
        # Feature 5: Service cost difference percentage
        service_monthly_avg = self.data.groupby(['year_month', 'Service'])['cost_amount'].mean().reset_index()
        service_monthly_avg.columns = ['year_month', 'Service', 'avg_amount']
        
        self.data = self.data.merge(service_monthly_avg, on=['year_month', 'Service'], how='left')
        self.data['percent_difference'] = ((self.data['cost_amount'] - self.data['avg_amount']) / self.data['avg_amount']) * 100
        self.data.loc[self.data['Service'] == 'دارو و ملزومات دارویی', 'percent_difference'] = 0
        self.data['percent_difference'] = self.data['percent_difference'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
        
        # Feature 6: Service cost change for provider
        service_provider_avg = self.data.groupby(['year_month', 'provider_name', 'Service'])['cost_amount'].mean().reset_index()
        service_provider_avg.columns = ['year_month', 'provider_name', 'Service', 'avg_amount_ser']
        
        service_overall_avg = self.data.groupby(['year_month', 'Service'])['cost_amount'].mean().reset_index()
        service_overall_avg.columns = ['year_month', 'Service', 'overall_avg_amount_ser']
        service_overall_avg['prev_avg_amount_serv'] = service_overall_avg.groupby('Service')['overall_avg_amount_ser'].shift(1)
        
        # Merge efficiently
        self.data = self.data.merge(service_provider_avg, on=['year_month', 'provider_name', 'Service'], how='left')
        self.data = self.data.merge(service_overall_avg[['year_month', 'Service', 'prev_avg_amount_serv']], on=['year_month', 'Service'], how='left')
        
        self.data['percent_diff_ser'] = ((self.data['avg_amount_ser'] - self.data['prev_avg_amount_serv']) / self.data['prev_avg_amount_serv']) * 100
        self.data.loc[self.data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_ser'] = 0
        self.data['percent_diff_ser'] = self.data['percent_diff_ser'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
        
        # Feature 8.1: Service cost change for patient
        service_patient_avg = self.data.groupby(['year_month', 'ID', 'Service'])['cost_amount'].mean().reset_index()
        service_patient_avg.columns = ['year_month', 'ID', 'Service', 'avg_amount_ser_patient']
        
        service_overall_patient_avg = self.data.groupby(['year_month', 'Service'])['cost_amount'].mean().reset_index()
        service_overall_patient_avg.columns = ['year_month', 'Service', 'overall_avg_amount_ser_patient']
        service_overall_patient_avg['prev_avg_amount_serv_patient'] = service_overall_patient_avg.groupby('Service')['overall_avg_amount_ser_patient'].shift(1)
        
        # Merge efficiently
        self.data = self.data.merge(service_patient_avg, on=['year_month', 'ID', 'Service'], how='left')
        self.data = self.data.merge(service_overall_patient_avg[['year_month', 'Service', 'prev_avg_amount_serv_patient']], on=['year_month', 'Service'], how='left')
        
        self.data['percent_diff_ser_patient'] = ((self.data['avg_amount_ser_patient'] - self.data['prev_avg_amount_serv_patient']) / self.data['prev_avg_amount_serv_patient']) * 100
        self.data.loc[self.data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_ser_patient'] = 0
        self.data['percent_diff_ser_patient'] = self.data['percent_diff_ser_patient'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
        
        # Feature 8.2: Service cost change (overall)
        service_overall_avg['prev_avg_amount_ser'] = service_overall_avg.groupby('Service')['overall_avg_amount_ser'].shift(1)
        self.data = self.data.merge(service_overall_avg[['year_month', 'Service', 'prev_avg_amount_ser']], on=['year_month', 'Service'], how='left')
        
        self.data['percent_diff_serv'] = ((self.data['cost_amount'] - self.data['prev_avg_amount_ser']) / self.data['prev_avg_amount_ser']) * 100
        self.data.loc[self.data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_serv'] = 0
        self.data['percent_diff_serv'] = self.data['percent_diff_serv'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
        
        # Clean up temporary data
        del service_monthly_avg, service_provider_avg, service_overall_avg, service_patient_avg, service_overall_patient_avg
        gc.collect()
    
    def _extract_specialty_features_efficiently(self):
        """Extract specialty-related features with memory optimization"""
        logger.info("Extracting specialty features efficiently...")
        
        # Feature 7: Specialty cost change for provider
        specialty_provider_avg = self.data.groupby(['year_month', 'provider_name', 'provider_specialty'])['cost_amount'].mean().reset_index()
        specialty_provider_avg.columns = ['year_month', 'provider_name', 'provider_specialty', 'avg_amount_spe']
        
        specialty_overall_avg = self.data.groupby(['year_month', 'provider_specialty'])['cost_amount'].mean().reset_index()
        specialty_overall_avg.columns = ['year_month', 'provider_specialty', 'overall_avg_amount_spe']
        specialty_overall_avg['prev_avg_amount_spe'] = specialty_overall_avg.groupby('provider_specialty')['overall_avg_amount_spe'].shift(1)
        
        # Merge efficiently
        self.data = self.data.merge(specialty_provider_avg, on=['year_month', 'provider_name', 'provider_specialty'], how='left')
        self.data = self.data.merge(specialty_overall_avg[['year_month', 'provider_specialty', 'prev_avg_amount_spe']], on=['year_month', 'provider_specialty'], how='left')
        
        self.data['percent_diff_spe'] = ((self.data['avg_amount_spe'] - self.data['prev_avg_amount_spe']) / self.data['prev_avg_amount_spe']) * 100
        self.data['percent_diff_spe'] = self.data['percent_diff_spe'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
        
        # Feature 7.2: Specialty cost change for provider (direct)
        self.data['percent_diff_spe2'] = ((self.data['cost_amount'] - self.data['prev_avg_amount_spe']) / self.data['prev_avg_amount_spe']) * 100
        self.data['percent_diff_spe2'] = self.data['percent_diff_spe2'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
        
        # Clean up temporary data
        del specialty_provider_avg, specialty_overall_avg
        gc.collect()
    
    def _extract_ratio_features_efficiently(self):
        """Extract ratio-related features with memory optimization"""
        logger.info("Extracting ratio features efficiently...")
        
        # Feature 9: Service ratio
        provider_service_count = self.data.groupby(['provider_name', 'Service']).size().reset_index(name='Count')
        provider_count = self.data['provider_name'].value_counts().reset_index()
        provider_count.columns = ['provider_name', 'TotalCount']
        
        # Merge efficiently
        merged = provider_service_count.merge(provider_count, on='provider_name')
        merged['Ratio'] = 1 - (merged['Count'] / merged['TotalCount'])
        merged.loc[merged['TotalCount'] == 1, 'Ratio'] = 0
        
        # Merge back to main data
        self.data = self.data.merge(merged[['provider_name', 'Service', 'Ratio']], on=['provider_name', 'Service'], how='left')
        
        # Clean up temporary data
        del provider_service_count, provider_count, merged
        gc.collect()
    
    def get_feature_columns(self) -> List[str]:
        """Get list of feature column names"""
        return self.feature_columns
    
    def prepare_features_for_prediction(self) -> pd.DataFrame:
        """Prepare features for model prediction"""
        features_df = self.data[self.feature_columns].copy()
        features_df.dropna(inplace=True)
        return features_df

# Keep the original class name for backward compatibility
FeatureExtractor = MemoryOptimizedFeatureExtractor
