"""
Memory-optimized prediction service for fraud detection API
سرویس پیش‌بینی بهینه‌سازی شده حافظه برای API تشخیص تقلب
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from scipy.stats import norm
from config.config import model_config
from core.exceptions import ModelNotReadyError
from .feature_extractor import FeatureExtractor
from functions.age_calculate_function import calculate_age
from functions.shamsi_to_miladi_function import shamsi_to_miladi
from functions.add_one_month_function import add_one_month
import logging
import gc
import os
import pickle
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MemoryOptimizedPredictionService:
    """Memory-optimized service for handling fraud predictions"""
    
    def __init__(self, data: pd.DataFrame = None, clf: IsolationForest = None, scaler: StandardScaler = None):
        self.data = data
        self.clf = clf
        self.scaler = scaler
        self.data_final = None
        self._feature_columns = [
            'unq_ratio_provider', 'unq_ratio_patient', 'percent_change_provider',
            'percent_change_patient', 'percent_difference', 'percent_diff_ser',
            'percent_diff_spe', 'percent_diff_spe2', 'percent_diff_ser_patient',
            'percent_diff_serv', 'Ratio'
        ]
        
        # Model persistence paths
        self.models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        self.model_path = os.path.join(self.models_dir, 'fraud_detection_model.pkl')
        self.scaler_path = os.path.join(self.models_dir, 'fraud_detection_scaler.pkl')
        self.metadata_path = os.path.join(self.models_dir, 'model_metadata.pkl')
        self.data_path = os.path.join(self.models_dir, 'processed_data.pkl')
        
        # Ensure models directory exists
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Try to load existing model first if persistence is enabled
        if model_config.enable_persistence:
            self._try_load_existing_model()
    
    def _try_load_existing_model(self) -> bool:
        """Try to load existing trained model and scaler"""
        try:
            if (os.path.exists(self.model_path) and 
                os.path.exists(self.scaler_path) and 
                os.path.exists(self.metadata_path) and
                os.path.exists(self.data_path)):
                
                logger.info("Found existing model files, attempting to load...")
                
                # Load model
                with open(self.model_path, 'rb') as f:
                    self.clf = pickle.load(f)
                
                # Load scaler
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                
                # Load metadata
                with open(self.metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                
                # Load processed data
                with open(self.data_path, 'rb') as f:
                    self.data_final = pickle.load(f)
                
                # Check if model is still valid (not too old)
                if self._is_model_fresh(metadata):
                    logger.info("Successfully loaded existing model and data")
                    return True
                else:
                    logger.info("Existing model is outdated, will retrain")
                    return False
            else:
                logger.info("No existing model files found")
                return False
                
        except Exception as e:
            logger.warning(f"Failed to load existing model: {str(e)}")
            return False
    
    def _is_model_fresh(self, metadata: Dict[str, Any]) -> bool:
        """Check if the model is still fresh (not too old)"""
        try:
            if 'last_trained' not in metadata:
                return False
            
            last_trained = metadata['last_trained']
            if isinstance(last_trained, str):
                last_trained = datetime.fromisoformat(last_trained)
            
            # Model is considered fresh if trained within configured days
            max_age_days = model_config.max_age_days
            age_threshold = datetime.now() - timedelta(days=max_age_days)
            
            is_fresh = last_trained > age_threshold
            logger.info(f"Model age: {datetime.now() - last_trained}, fresh: {is_fresh}")
            
            return is_fresh
            
        except Exception as e:
            logger.warning(f"Error checking model freshness: {str(e)}")
            return False
    
    def _save_model(self) -> None:
        """Save trained model, scaler, metadata, and processed data"""
        try:
            if self.clf is not None and self.scaler is not None and self.data_final is not None:
                logger.info("Saving trained model and data...")
                
                # Save model
                with open(self.model_path, 'wb') as f:
                    pickle.dump(self.clf, f)
                
                # Save scaler
                with open(self.scaler_path, 'wb') as f:
                    pickle.dump(self.scaler, f)
                
                # Save processed data
                with open(self.data_path, 'wb') as f:
                    pickle.dump(self.data_final, f)
                
                # Save metadata
                metadata = {
                    'last_trained': datetime.now().isoformat(),
                    'model_type': 'IsolationForest',
                    'n_estimators': model_config.n_estimators,
                    'max_samples': model_config.max_samples,
                    'max_features': model_config.max_features,
                    'contamination': model_config.contamination,
                    'training_samples': len(self.data_final) if self.data_final is not None else 0,
                    'feature_count': len(self._feature_columns)
                }
                
                with open(self.metadata_path, 'wb') as f:
                    pickle.dump(metadata, f)
                
                logger.info("Model and data saved successfully")
                
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
    
    def force_retrain(self) -> None:
        """Force model retraining by clearing existing model"""
        try:
            logger.info("Forcing model retraining...")
            
            # Clear existing model
            self.clf = None
            self.scaler = None
            self.data_final = None
            
            # Remove existing model files
            for file_path in [self.model_path, self.scaler_path, self.metadata_path, self.data_path]:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Removed {file_path}")
            
            logger.info("Model cleared, will retrain on next training call")
            
        except Exception as e:
            logger.error(f"Error forcing retrain: {str(e)}")
    
    def is_ready(self) -> bool:
        """Check if the model is ready for predictions"""
        return all([
            self.clf is not None, 
            self.scaler is not None, 
            self.data_final is not None
        ])
    
    def train_model(self, data: pd.DataFrame) -> None:
        """
        Train the Isolation Forest model with memory optimization
        
        Args:
            data: Training data with features
        """
        try:
            logger.info("Starting memory-optimized model training...")
            
            # Store reference to original data
            self.data = data
            
            # Extract features efficiently
            feature_extractor = FeatureExtractor(data)
            self.data = feature_extractor.extract_all_features()
            
            # Prepare features for training - only keep necessary columns
            self.data_final = self.data[self._feature_columns].copy()
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
            
            # Attach metadata columns efficiently
            self._attach_metadata_columns_efficiently()
            
            # Clean up intermediate data
            gc.collect()
            
            # Save the trained model if persistence is enabled
            if model_config.auto_save:
                self._save_model()
            
            logger.info("Memory-optimized model training completed successfully")
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def train_model_streaming(self, features_df: pd.DataFrame, metadata_df: pd.DataFrame) -> None:
        """
        Train the Isolation Forest model with streaming data
        
        Args:
            features_df: DataFrame with extracted features
            metadata_df: DataFrame with metadata columns
        """
        try:
            logger.info("Starting streaming model training...")
            
            # Prepare features for training
            self.data_final = features_df.copy()
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
            self._attach_metadata_columns_streaming(metadata_df)
            
            # Clean up intermediate data
            gc.collect()
            
            # Save the trained model if persistence is enabled
            if model_config.auto_save:
                self._save_model()
            
            logger.info("Streaming model training completed successfully")
            
        except Exception as e:
            logger.error(f"Error training model with streaming data: {str(e)}")
            raise
    
    def predict_new_prescription(self, prescription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict fraud for a new prescription with memory optimization
        
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
            logger.info(f"Starting prediction for prescription ID: {prescription_data.get('ID', 'unknown')}")
            
            # Create new sample DataFrame efficiently
            new_sample = pd.DataFrame([prescription_data])
            logger.info(f"Created new_sample DataFrame with shape: {new_sample.shape}")
            
            # Convert dates efficiently
            new_sample['Adm_date'] = new_sample['Adm_date'].apply(shamsi_to_miladi)
            new_sample['Adm_date'] = pd.to_datetime(new_sample['Adm_date'])
            new_sample['age'] = new_sample['jalali_date'].apply(calculate_age)
            new_sample['year_month'] = new_sample['Adm_date'].dt.to_period('M')
            logger.info(f"Processed dates and created year_month column")
            
            # Select required fields for feature calculation - use minimal data
            features1 = ['ID', 'jalali_date', 'Adm_date', 'Service', 'provider_name', 
                        'provider_specialty', 'cost_amount', 'age', 'year_month']
            
            # Check if self.data is available, if not use self.data_final
            logger.info(f"self.data is None: {self.data is None}")
            if self.data is not None:
                # Create a minimal copy of data for feature calculation
                data1 = self.data[features1].copy()
                logger.info(f"Using self.data for feature calculation, shape: {data1.shape}")
            else:
                # If self.data is None (model loaded from disk), create a minimal dataset
                # from the available columns in data_final
                available_features = [col for col in features1 if col in self.data_final.columns]
                logger.info(f"Available features in data_final: {available_features}")
                if available_features:
                    data1 = self.data_final[available_features].copy()
                    logger.info(f"Using data_final for feature calculation, shape: {data1.shape}")
                else:
                    # If no features available, create a minimal dataset with just the new record
                    # This ensures feature functions have some data to work with
                    data1 = new_sample[features1].copy()
                    logger.info(f"Using new_sample for feature calculation, shape: {data1.shape}")
            
            # Calculate features using helper function
            logger.info("Starting feature calculation...")
            self._calculate_all_features_efficiently(data1, new_sample)
            logger.info("Feature calculation completed")
            
            # Select features for prediction
            new_sample_final = new_sample[self._feature_columns].copy()
            
            # Normalize features efficiently
            normalized_array = self.scaler.transform(new_sample_final)
            
            # Predict
            y_new_pred = self.clf.predict(normalized_array)
            scores_new = self.clf.decision_function(normalized_array)
            
            # Calculate risk scores efficiently
            probabilities = norm.cdf(normalized_array)
            scaled_risk_scores = (probabilities * 100).flatten()
            
            # Store features before cleanup and ensure JSON serialization
            features_dict = new_sample_final.iloc[0].to_dict()
            
            # Convert numpy types to Python native types for JSON serialization
            def convert_to_json_serializable(obj):
                """Convert numpy types and other non-serializable types to JSON-serializable types"""
                if hasattr(obj, 'item'):  # numpy scalar
                    return obj.item()
                elif hasattr(obj, 'tolist'):  # numpy array
                    return obj.tolist()
                elif isinstance(obj, (np.integer, np.floating)):
                    return obj.item()
                elif isinstance(obj, np.bool_):
                    return bool(obj)
                elif isinstance(obj, (np.ndarray,)):
                    return obj.tolist()
                else:
                    return obj
            
            # Convert all values in features_dict to JSON-serializable types
            features_dict = {k: convert_to_json_serializable(v) for k, v in features_dict.items()}
            
            # Prepare response data
            response_data = {
                'prediction': int(y_new_pred[0]),
                'score': float(scores_new[0]),
                'is_fraud': bool(y_new_pred[0] == -1),  # Ensure boolean is Python bool, not numpy bool
                'risk_scores': scaled_risk_scores.tolist(),
                'features': features_dict
            }
            
            # Debug: Check for any remaining non-serializable types
            logger.info(f"Response data types: {[(k, type(v)) for k, v in response_data.items()]}")
            
            # Clean up temporary data
            del data1, new_sample
            gc.collect()
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error predicting new prescription: {str(e)}")
            raise
    
    def _calculate_all_features_efficiently(self, data1: pd.DataFrame, new_sample: pd.DataFrame) -> None:
        """Calculate all features for the new sample with memory optimization"""
        try:
            # Import feature calculation functions
            from functions.ftr_1_function import unique_providers_nf
            from functions.ftr_2_function import unique_patients_nf
            from functions.ftr_3_3_function import percent_change_provider_nf
            from functions.ftr_4_function import percent_change_patient_nf
            from functions.ftr_5_function import percent_difference_nf
            from functions.ftr_6_function import percent_diff_ser_nf
            from functions.ftr_7_function import percent_diff_spe_nf
            from functions.ftr_7_2_function import percent_diff_spe2_nf
            from functions.ftr_8_1_function import percent_diff_ser_patient_nf
            from functions.ftr_8_2_function import percent_diff_serv_nf
            from functions.ftr_9_function import ratio_nf
            
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
                try:
                    result = func(data1, new_sample)
                    if result is not None and hasattr(result, '__getitem__'):
                        new_sample[feature_name] = result[feature_name]
                    else:
                        logger.warning(f"Feature function {func.__name__} returned None or invalid result, setting {feature_name} to 0")
                        new_sample[feature_name] = 0
                except Exception as feature_error:
                    logger.warning(f"Error calculating feature {feature_name} with {func.__name__}: {str(feature_error)}, setting to 0")
                    new_sample[feature_name] = 0
                
        except Exception as e:
            logger.error(f"Error calculating features: {str(e)}")
            raise
    
    def _attach_metadata_columns_efficiently(self) -> None:
        """Attach metadata columns to data_final efficiently for chart generation"""
        meta_columns = [
            'Adm_date', 'gender', 'age', 'Service', 'province',
            'Ins_Cover', 'Invice-type', 'Type_Medical_Record',
            'provider_name', 'ID'
        ]
        
        # Only attach columns that exist in the original data
        available_meta_columns = [col for col in meta_columns if col in self.data.columns]
        
        for col in available_meta_columns:
            self.data_final[col] = self.data.loc[self.data_final.index, col]
    
    def _attach_metadata_columns_streaming(self, metadata_df: pd.DataFrame) -> None:
        """Attach metadata columns from streaming data"""
        try:
            # Ensure metadata_df has the same index as data_final
            if len(metadata_df) == len(self.data_final):
                # Align metadata with features
                metadata_df = metadata_df.reset_index(drop=True)
                self.data_final = self.data_final.reset_index(drop=True)
                
                # Attach metadata columns
                meta_columns = [
                    'Adm_date', 'gender', 'age', 'Service', 'province',
                    'Ins_Cover', 'Invice-type', 'Type_Medical_Record',
                    'provider_name', 'ID'
                ]
                
                available_meta_columns = [col for col in meta_columns if col in metadata_df.columns]
                
                for col in available_meta_columns:
                    self.data_final[col] = metadata_df[col]
                    
                logger.info(f"Attached {len(available_meta_columns)} metadata columns")
            else:
                logger.warning(f"Metadata length ({len(metadata_df)}) doesn't match features length ({len(self.data_final)})")
                
        except Exception as e:
            logger.error(f"Error attaching metadata columns: {str(e)}")
    
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
            'feature_count': len(self._feature_columns)
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
            'features_count': len(self._feature_columns)
        }
    
    def cleanup_memory(self):
        """Clean up memory by removing unnecessary data"""
        try:
            logger.info("Cleaning up prediction service memory...")
            
            # Remove original data if data_final contains all necessary information
            if self.data_final is not None and self.data is not None:
                # Check if data_final has all necessary columns for charts
                required_columns = ['Adm_date', 'gender', 'age', 'Service', 'province',
                                  'Ins_Cover', 'Invice-type', 'Type_Medical_Record',
                                  'provider_name', 'ID', 'prediction']
                
                if all(col in self.data_final.columns for col in required_columns):
                    self.data = None
                    gc.collect()
                    logger.info("Removed original data from prediction service")
            
        except Exception as e:
            logger.error(f"Error during prediction service memory cleanup: {str(e)}")

# Keep the original class name for backward compatibility
PredictionService = MemoryOptimizedPredictionService
