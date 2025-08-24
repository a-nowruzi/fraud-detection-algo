"""
Feature extraction service for fraud detection
سرویس استخراج ویژگی‌ها برای تشخیص تقلب
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from utils import safe_division, calculate_percentage_change, performance_monitor
from config import app_config
import logging

logger = logging.getLogger(__name__)

class FeatureExtractor:
    """Service for extracting features from prescription data"""
    
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
        """Extract all features from the dataset"""
        try:
            logger.info("Starting feature extraction...")
            
            # Extract features using helper methods
            self._extract_provider_features()
            self._extract_patient_features()
            self._extract_service_features()
            self._extract_specialty_features()
            self._extract_ratio_features()
            
            logger.info("Feature extraction completed successfully")
            return self.data
            
        except Exception as e:
            logger.error(f"Error in feature extraction: {str(e)}")
            raise
    
    def _extract_provider_features(self):
        """Extract provider-related features"""
        logger.info("Extracting provider features...")
        
        # Feature 1: Ratio of total providers to unique providers
        providers_count_per_month = self.data.groupby(['year_month', 'ID']).agg(
            total_providers_monthly=('provider_name', 'count')
        ).reset_index()
        self.data = self.data.merge(providers_count_per_month, on=['year_month', 'ID'], how='left')
        
        unique_providers_per_month = self.data.groupby(['year_month', 'ID']).agg(
            unique_providers=('provider_name', 'nunique')
        ).reset_index()
        self.data = self.data.merge(unique_providers_per_month, on=['year_month', 'ID'], how='left')
        
        self.data['unq_ratio_provider'] = self.data.apply(
            lambda row: safe_division(row['total_providers_monthly'], row['unique_providers']), 
            axis=1
        )
    
    def _extract_patient_features(self):
        """Extract patient-related features"""
        logger.info("Extracting patient features...")
        
        # Feature 2: Ratio of total patients to unique patients
        patients_count_per_month = self.data.groupby(['year_month', 'provider_name']).agg(
            total_patients_monthly=('ID', 'count')
        ).reset_index()
        self.data = self.data.merge(patients_count_per_month, on=['year_month', 'provider_name'], how='left')
        
        unique_patients_per_month = self.data.groupby(['year_month', 'provider_name']).agg(
            unique_patients=('ID', 'nunique')
        ).reset_index()
        self.data = self.data.merge(unique_patients_per_month, on=['year_month', 'provider_name'], how='left')
        
        self.data['unq_ratio_patient'] = self.data.apply(
            lambda row: safe_division(row['total_patients_monthly'], row['unique_patients']), 
            axis=1
        )
        
        # Feature 3 & 4: Provider and Patient cost change percentage
        self._extract_cost_change_features()
    
    def _extract_cost_change_features(self):
        """Extract cost change percentage features"""
        logger.info("Extracting cost change features...")
        
        # Provider cost change
        monthly_means = self.data.groupby(['year_month', 'provider_name']).agg(
            mean_amount_provider=('cost_amount', 'mean')
        ).reset_index()
        
        monthly_means['previous_mean_amount_provider_1'] = monthly_means.groupby('provider_name')['mean_amount_provider'].shift(1)
        monthly_means['previous_mean_amount_provider_2'] = monthly_means.groupby('provider_name')['mean_amount_provider'].shift(2)
        monthly_means['average_previous_mean_provider'] = monthly_means[['previous_mean_amount_provider_1', 'previous_mean_amount_provider_2']].mean(axis=1)
        
        monthly_means['percent_change_provider'] = monthly_means.apply(
            lambda row: calculate_percentage_change(
                row['mean_amount_provider'], 
                row['average_previous_mean_provider'],
                app_config.max_percentage_change
            ), 
            axis=1
        )
        
        self.data = self.data.merge(monthly_means, on=['year_month', 'provider_name'], how='left', suffixes=('', '_monthly'))
        
        # Patient cost change
        monthly_means = self.data.groupby(['year_month', 'ID']).agg(
            mean_amount_patient=('cost_amount', 'mean')
        ).reset_index()
        
        monthly_means['previous_mean_amount_patient_1'] = monthly_means.groupby('ID')['mean_amount_patient'].shift(1)
        monthly_means['previous_mean_amount_patient_2'] = monthly_means.groupby('ID')['mean_amount_patient'].shift(2)
        monthly_means['average_previous_mean_patient'] = monthly_means[['previous_mean_amount_patient_1', 'previous_mean_amount_patient_2']].mean(axis=1)
        
        monthly_means['percent_change_patient'] = monthly_means.apply(
            lambda row: calculate_percentage_change(
                row['mean_amount_patient'], 
                row['average_previous_mean_patient'],
                app_config.max_percentage_change
            ), 
            axis=1
        )
        
        self.data = self.data.merge(monthly_means, on=['year_month', 'ID'], how='left', suffixes=('', '_monthly'))
    
    def _extract_service_features(self):
        """Extract service-related features"""
        logger.info("Extracting service features...")
        
        # Feature 5: Service cost difference percentage
        monthly_avg = self.data.groupby(['year_month', 'Service']).agg(avg_amount=('cost_amount', 'mean')).reset_index()
        self.data = self.data.merge(monthly_avg, on=['year_month', 'Service'], how='left', suffixes=('', '_monthly'))
        self.data['percent_difference'] = ((self.data['cost_amount'] - self.data['avg_amount']) / self.data['avg_amount']) * 100
        self.data.loc[self.data['Service'] == 'دارو و ملزومات دارویی', 'percent_difference'] = 0
        self.data['percent_difference'] = self.data['percent_difference'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
        
        # Feature 6: Service cost change for provider
        monthly_avg_per_provider = self.data.groupby(['year_month', 'provider_name', 'Service']).agg(
            avg_amount_ser=('cost_amount', 'mean')
        ).reset_index()
        
        monthly_avg_overall = self.data.groupby(['year_month', 'Service']).agg(
            overall_avg_amount_ser=('cost_amount', 'mean')
        ).reset_index()
        
        monthly_avg_overall['prev_avg_amount_serv'] = monthly_avg_overall.groupby('Service')['overall_avg_amount_ser'].shift(1)
        self.data = self.data.merge(monthly_avg_per_provider[['year_month', 'provider_name', 'Service', 'avg_amount_ser']], 
                     on=['year_month', 'provider_name', 'Service'], how='left', suffixes=('', '_provider'))
        self.data = self.data.merge(monthly_avg_overall[['year_month', 'Service', 'prev_avg_amount_serv']], 
                     on=['year_month', 'Service'], how='left')
        self.data['percent_diff_ser'] = ((self.data['avg_amount_ser'] - self.data['prev_avg_amount_serv']) / self.data['prev_avg_amount_serv']) * 100
        self.data.loc[self.data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_ser'] = 0
        self.data['percent_diff_ser'] = self.data['percent_diff_ser'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
        
        # Feature 8.1: Service cost change for patient
        monthly_avg_per_patient = self.data.groupby(['year_month', 'ID', 'Service']).agg(
            avg_amount_ser_patient=('cost_amount', 'mean')
        ).reset_index()
        
        monthly_avg_overall_patient = self.data.groupby(['year_month', 'Service']).agg(
            overall_avg_amount_ser_patient=('cost_amount', 'mean')
        ).reset_index()
        
        monthly_avg_overall_patient['prev_avg_amount_serv_patient'] = monthly_avg_overall_patient.groupby('Service')['overall_avg_amount_ser_patient'].shift(1)
        self.data = self.data.merge(monthly_avg_per_patient[['year_month', 'ID', 'Service', 'avg_amount_ser_patient']], 
                     on=['year_month', 'ID', 'Service'], how='left', suffixes=('', '_patient'))
        self.data = self.data.merge(monthly_avg_overall_patient[['year_month', 'Service', 'prev_avg_amount_serv_patient']], 
                     on=['year_month', 'Service'], how='left')
        self.data['percent_diff_ser_patient'] = ((self.data['avg_amount_ser_patient'] - self.data['prev_avg_amount_serv_patient']) / self.data['prev_avg_amount_serv_patient']) * 100
        self.data.loc[self.data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_ser_patient'] = 0
        self.data['percent_diff_ser_patient'] = self.data['percent_diff_ser_patient'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
        
        # Feature 8.2: Service cost change (overall)
        monthly_avg_overall = self.data.groupby(['year_month', 'Service']).agg(
            overall_avg_amount_ser=('cost_amount', 'mean')
        ).reset_index()
        
        monthly_avg_overall['prev_avg_amount_ser'] = monthly_avg_overall.groupby('Service')['overall_avg_amount_ser'].shift(1)
        self.data = self.data.merge(monthly_avg_overall[['year_month', 'Service', 'prev_avg_amount_ser']], 
                     on=['year_month', 'Service'], how='left')
        self.data['percent_diff_serv'] = ((self.data['cost_amount'] - self.data['prev_avg_amount_ser']) / self.data['prev_avg_amount_ser']) * 100
        self.data.loc[self.data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_serv'] = 0
        self.data['percent_diff_serv'] = self.data['percent_diff_serv'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
    
    def _extract_specialty_features(self):
        """Extract specialty-related features"""
        logger.info("Extracting specialty features...")
        
        # Feature 7: Specialty cost change for provider
        monthly_avg_per_provider_spe = self.data.groupby(['year_month', 'provider_name', 'provider_specialty']).agg(
            avg_amount_spe=('cost_amount', 'mean')
        ).reset_index()
        
        monthly_avg_overall_spe = self.data.groupby(['year_month', 'provider_specialty']).agg(
            overall_avg_amount_spe=('cost_amount', 'mean')
        ).reset_index()
        
        monthly_avg_overall_spe['prev_avg_amount_spe'] = monthly_avg_overall_spe.groupby('provider_specialty')['overall_avg_amount_spe'].shift(1)
        self.data = self.data.merge(monthly_avg_per_provider_spe[['year_month', 'provider_name', 'provider_specialty', 'avg_amount_spe']], 
                     on=['year_month', 'provider_name', 'provider_specialty'], how='left', suffixes=('', '_provider'))
        self.data = self.data.merge(monthly_avg_overall_spe[['year_month', 'provider_specialty', 'prev_avg_amount_spe']], 
                     on=['year_month', 'provider_specialty'], how='left')
        self.data['percent_diff_spe'] = ((self.data['avg_amount_spe'] - self.data['prev_avg_amount_spe']) / self.data['prev_avg_amount_spe']) * 100
        self.data['percent_diff_spe'] = self.data['percent_diff_spe'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
        
        # Feature 7.2: Specialty cost change for provider (direct)
        self.data['percent_diff_spe2'] = ((self.data['cost_amount'] - self.data['prev_avg_amount_spe']) / self.data['prev_avg_amount_spe']) * 100
        self.data['percent_diff_spe2'] = self.data['percent_diff_spe2'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
    
    def _extract_ratio_features(self):
        """Extract ratio-related features"""
        logger.info("Extracting ratio features...")
        
        # Feature 9: Service ratio
        provider_service_count = self.data.groupby(['provider_name', 'Service']).size().reset_index(name='Count')
        
        provider_count = self.data['provider_name'].value_counts().reset_index()
        provider_count.columns = ['provider_name', 'TotalCount']
        
        merged = pd.merge(provider_service_count, provider_count, on='provider_name')
        merged['Ratio'] = 1 - (merged['Count'] / merged['TotalCount'])
        merged.loc[merged['TotalCount'] == 1, 'Ratio'] = 0
        self.data = pd.merge(self.data, merged[['provider_name', 'Service', 'Ratio']], 
                   on=['provider_name', 'Service'], how='left')
    
    def get_feature_columns(self) -> List[str]:
        """Get list of feature column names"""
        return self.feature_columns
    
    def prepare_features_for_prediction(self) -> pd.DataFrame:
        """Prepare features for model prediction"""
        features_df = self.data[self.feature_columns].copy()
        features_df.dropna(inplace=True)
        return features_df
