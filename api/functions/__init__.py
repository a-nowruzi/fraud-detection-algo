"""
Feature Extraction Functions Package

This package contains all the feature extraction functions used in the fraud detection system.
Each function is designed to extract specific features from prescription data.
"""

# Import all feature functions for easy access
from .age_calculate_function import calculate_age
from .add_one_month_function import add_one_month
from .shamsi_to_miladi_function import shamsi_to_miladi
from .normalazation_function import normalize_features, normalize_single_record

# Feature extraction functions
from .ftr_1_function import unique_providers_nf
from .ftr_2_function import unique_patients_nf
from .ftr_3_3_function import percent_change_provider_nf
from .ftr_4_function import percent_change_patient_nf
from .ftr_5_function import percent_difference_nf
from .ftr_6_function import percent_diff_ser_nf
from .ftr_7_function import percent_diff_spe_nf
from .ftr_7_2_function import percent_diff_spe2_nf
from .ftr_8_1_function import percent_diff_ser_patient_nf
from .ftr_8_2_function import percent_diff_serv_nf
from .ftr_9_function import ratio_nf

__all__ = [
    # Utility functions
    'calculate_age',
    'add_one_month',
    'shamsi_to_miladi',
    'normalize_features',
    'normalize_single_record',
    
    # Feature extraction functions
    'unique_providers_nf',
    'unique_patients_nf',
    'percent_change_provider_nf',
    'percent_change_patient_nf',
    'percent_difference_nf',
    'percent_diff_ser_nf',
    'percent_diff_spe_nf',
    'percent_diff_spe2_nf',
    'percent_diff_ser_patient_nf',
    'percent_diff_serv_nf',
    'ratio_nf',
]

__version__ = '1.0.0'
__author__ = 'Fraud Detection Team'
__description__ = 'Feature extraction functions for medical fraud detection'
