"""
Prediction service for fraud detection API
سرویس پیش‌بینی برای API تشخیص تقلب
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from scipy.stats import norm
from config import model_config
from exceptions import ModelNotReadyError
from services.feature_extractor import FeatureExtractor
from age_calculate_function import calculate_age
from shamsi_to_miladi_function import shamsi_to_miladi
from add_one_month_function import add_one_month
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    """Service for handling fraud predictions"""
    
    def __init__(self, data: pd.DataFrame = None, clf: IsolationForest = None, scaler: StandardScaler = None):
        self.data = data
        self.clf = clf
        self.scaler = scaler
        self.data_final = None
    
    def is_ready(self) -> bool:
        """Check if the model is ready for predictions"""
        return all([
            self.data is not None, 
            self.clf is not None, 
            self.scaler is not None, 
            self.data_final is not None
        ])
    
    def train_model(self, data: pd.DataFrame) -> None:
        """
        Train the Isolation Forest model
        
        Args:
            data: Training data with features
        """
        try:
            logger.info("Starting model training...")
            
            # Extract features
            feature_extractor = FeatureExtractor(data)
            self.data = feature_extractor.extract_all_features()
            
            # Prepare features for training
            features = feature_extractor.get_feature_columns()
            self.data_final = self.data[features].copy()
            self.data_final.dropna(inplace=True)
            
            # Standardize features
            self.scaler = StandardScaler()
            X = self.scaler.fit_transform(self.data_final)
            
            # Train Isolation Forest
            self.clf = IsolationForest(
                n_estimators=model_config.n_estimators,
                max_samples=model_config.max_samples,
                max_features=model_config.max_features,
                contamination=model_config.contamination,
                random_state=model_config.random_state
            )
            self.clf.fit(X)
            
            # Predict on training data
            y_pred = self.clf.predict(X)
            self.data_final['prediction'] = y_pred
            
            # Attach metadata columns
            self._attach_metadata_columns()
            
            logger.info("Model training completed successfully")
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def predict_new_prescription(self, prescription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict fraud for a new prescription
        
        Args:
            prescription_data: Prescription data to predict
            
        Returns:
            Prediction results with scores and features
            
        Raises:
            ModelNotReadyError: If model is not ready
        """
        if not self.is_ready():
            raise ModelNotReadyError()
        
        try:
            # Create new sample DataFrame
            new_sample = pd.DataFrame([prescription_data])
            
            # Convert dates
            new_sample['Adm_date'] = new_sample['Adm_date'].apply(shamsi_to_miladi)
            new_sample['Adm_date'] = pd.to_datetime(new_sample['Adm_date'])
            new_sample['age'] = new_sample['jalali_date'].apply(calculate_age)
            new_sample['year_month'] = new_sample['Adm_date'].dt.to_period('M')
            
            # Select required fields for feature calculation
            features1 = ['ID', 'jalali_date', 'Adm_date', 'Service', 'provider_name', 
                        'provider_specialty', 'cost_amount', 'age', 'year_month']
            data1 = self.data[features1].copy()
            
            # Calculate features using helper function
            self._calculate_all_features(data1, new_sample)
            
            # Select features for prediction
            features = [
                'unq_ratio_provider', 'unq_ratio_patient', 'percent_change_provider',
                'percent_change_patient', 'percent_difference', 'percent_diff_ser',
                'percent_diff_spe', 'percent_diff_spe2', 'percent_diff_ser_patient',
                'percent_diff_serv', 'Ratio'
            ]
            
            new_sample_final = new_sample[features].copy()
            
            # Normalize features
            full_data = pd.concat([self.data_final, new_sample_final], ignore_index=True)
            scaler_temp = StandardScaler()
            scaler_temp.fit(full_data)
            normalized_array = scaler_temp.transform(new_sample_final)
            
            # Predict
            y_new_pred = self.clf.predict(normalized_array)
            scores_new = self.clf.decision_function(normalized_array)
            
            # Calculate risk scores
            probabilities = norm.cdf(normalized_array)
            scaled_risk_scores = (probabilities * 100).flatten()
            
            return {
                'prediction': int(y_new_pred[0]),
                'score': float(scores_new[0]),
                'is_fraud': y_new_pred[0] == -1,
                'risk_scores': scaled_risk_scores.tolist(),
                'features': new_sample_final.iloc[0].to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error predicting new prescription: {str(e)}")
            raise
    
    def _calculate_all_features(self, data1: pd.DataFrame, new_sample: pd.DataFrame) -> None:
        """Calculate all features for the new sample"""
        try:
            # Import feature calculation functions
            from ftr_1_function import unique_providers_nf
            from ftr_2_function import unique_patients_nf
            from ftr_3_3_function import percent_change_provider_nf
            from ftr_4_function import percent_change_patient_nf
            from ftr_5_function import percent_difference_nf
            from ftr_6_function import percent_diff_ser_nf
            from ftr_7_function import percent_diff_spe_nf
            from ftr_7_2_function import percent_diff_spe2_nf
            from ftr_8_1_function import percent_diff_ser_patient_nf
            from ftr_8_2_function import percent_diff_serv_nf
            from ftr_9_function import ratio_nf
            
            feature_functions = [
                (unique_providers_nf, 'unq_ratio_provider'),
                (unique_patients_nf, 'unq_ratio_patient'),
                (percent_change_provider_nf, 'percent_change_provider'),
                (percent_change_patient_nf, 'percent_change_patient'),
                (percent_difference_nf, 'percent_difference'),
                (percent_diff_ser_nf, 'percent_diff_ser'),
                (percent_diff_spe_nf, 'percent_diff_spe'),
                (percent_diff_spe2_nf, 'percent_diff_spe2'),
                (percent_diff_ser_patient_nf, 'percent_diff_ser_patient'),
                (percent_diff_serv_nf, 'percent_diff_serv'),
                (ratio_nf, 'Ratio')
            ]
            
            for func, feature_name in feature_functions:
                result = func(data1, new_sample)
                new_sample[feature_name] = result[feature_name]
                
        except Exception as e:
            logger.error(f"Error calculating features: {str(e)}")
            raise
    
    def _attach_metadata_columns(self) -> None:
        """Attach metadata columns to data_final for chart generation"""
        meta_columns = [
            'Adm_date', 'gender', 'age', 'Service', 'province',
            'Ins_Cover', 'Invice-type', 'Type_Medical_Record',
            'provider_name', 'ID'
        ]
        for col in meta_columns:
            if col in self.data.columns:
                self.data_final[col] = self.data.loc[self.data_final.index, col]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the trained model"""
        if not self.is_ready():
            return {'status': 'not_ready'}
        
        return {
            'status': 'ready',
            'model_type': 'IsolationForest',
            'n_estimators': model_config.n_estimators,
            'max_samples': model_config.max_samples,
            'max_features': model_config.max_features,
            'contamination': model_config.contamination,
            'training_samples': len(self.data_final),
            'feature_count': len(self.data_final.columns) - 1  # Exclude prediction column
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get prediction statistics"""
        if not self.is_ready():
            return {'error': 'Model not ready'}
        
        total_prescriptions = len(self.data_final)
        fraud_prescriptions = len(self.data_final[self.data_final['prediction'] == -1])
        normal_prescriptions = len(self.data_final[self.data_final['prediction'] == 1])
        fraud_percentage = (fraud_prescriptions / total_prescriptions) * 100
        
        return {
            'total_prescriptions': total_prescriptions,
            'fraud_prescriptions': fraud_prescriptions,
            'normal_prescriptions': normal_prescriptions,
            'fraud_percentage': round(fraud_percentage, 2),
            'model_contamination': model_config.contamination,
            'features_count': 11
        }
