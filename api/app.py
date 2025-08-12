from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from flasgger import Swagger
import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import json
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from scipy.stats import norm
# Removed unused imports to reduce warnings
import matplotlib.dates as mdates

# Import custom functions
from age_calculate_function import calculate_age
from shamsi_to_miladi_function import shamsi_to_miladi
from add_one_month_function import add_one_month
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

# Suppress warnings
warnings.filterwarnings('ignore')
pd.set_option('display.max_column', 50)
pd.set_option('display.max_rows', 100)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Swagger configuration
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Medical Fraud Detection API",
        "description": "API for detecting fraudulent medical prescriptions. برای مشاهده مستندات تعاملی به مسیر /docs مراجعه کنید.",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": ["http"],
    "consumes": ["application/json"],
    "produces": ["application/json"]
}

app.config['SWAGGER'] = {
    'title': 'Medical Fraud Detection API',
    'uiversion': 3,
}

swagger = Swagger(app, template=swagger_template, config={
    'headers': [],
    'specs': [
        {
            'endpoint': 'apispec_1',
            'route': '/apispec_1.json',
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True,
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': '/docs/'
})

# Global state management
class AppState:
    """Centralized state management for the application"""
    def __init__(self):
        self.data = None
        self.clf = None
        self.scaler = None
        self.data_final = None
    
    def is_ready(self):
        """Check if all components are loaded"""
        return all([self.data is not None, self.clf is not None, 
                   self.scaler is not None, self.data_final is not None])

# Initialize application state
app_state = AppState()

def load_and_prepare_data():
    """Load and prepare the dataset"""
    try:
        print("Loading dataset...")
        app_state.data = pd.read_csv('DataSEt_FD7.csv')
        
        # Use utility functions for cleaning numeric columns
        from utils import clean_numeric_column, memory_usage_optimizer
        
        # Clean numeric columns
        app_state.data['cost_amount'] = clean_numeric_column(app_state.data['cost_amount'], 'cost_amount')
        app_state.data['ded_amount'] = clean_numeric_column(app_state.data['ded_amount'], 'ded_amount')
        app_state.data['confirmed_amount'] = clean_numeric_column(app_state.data['confirmed_amount'], 'confirmed_amount')
    
        # Fill missing provider names
        app_state.data['provider_name'] = app_state.data['provider_name'].fillna(app_state.data['ref_code'])
        app_state.data['provider_name'] = app_state.data['provider_name'].fillna(app_state.data['ref_name'])
        
        # Load specialties
        specialties = pd.read_csv('specialties.csv')
        merged_data = app_state.data.merge(specialties, on='Service', how='left')
        app_state.data['provider_specialty'] = app_state.data['provider_specialty'].combine_first(merged_data['specialty'])
        
        # Add age column using improved function
        app_state.data['age'] = app_state.data['jalali_date'].apply(calculate_age)
        
        # Convert dates using improved functions
        app_state.data['Adm_date'] = app_state.data['Adm_date'].apply(shamsi_to_miladi)
        app_state.data['confirm_date'] = app_state.data['confirm_date'].apply(shamsi_to_miladi)
        app_state.data['confirm_date'] = app_state.data['confirm_date'].fillna(app_state.data['Adm_date'].apply(add_one_month))
        
        # Reset confirmed amount
        app_state.data['confirmed_amount'] = app_state.data['confirmed_amount'].fillna(0)
        app_state.data['record_id'] = range(1, len(app_state.data) + 1)
        app_state.data['Adm_date'] = pd.to_datetime(app_state.data['Adm_date'])
        app_state.data['year_month'] = app_state.data['Adm_date'].dt.to_period('M')
        
        # Ensure consistent data types for key columns before feature extraction
        app_state.data['ID'] = app_state.data['ID'].astype(str)
        app_state.data['provider_name'] = app_state.data['provider_name'].astype(str)
        app_state.data['Service'] = app_state.data['Service'].astype(str)
        app_state.data['provider_specialty'] = app_state.data['provider_specialty'].astype(str)
        app_state.data['year_month'] = app_state.data['year_month'].astype(str)
        
        # Optimize memory usage
        app_state.data = memory_usage_optimizer(app_state.data)
        
        print("Extracting features...")
        extract_features()
        
        print("Training model...")
        train_model()
        
        print("Data and model loaded successfully!")
        
    except Exception as e:
        print(f"Error loading and preparing data: {str(e)}")
        raise

def extract_features():
    """Extract all features from the dataset"""
    try:
        # Use improved utility functions for safer calculations
        from utils import safe_division, calculate_percentage_change
        
        # Extract features using helper functions to reduce code duplication
        _extract_provider_features()
        _extract_patient_features()
        _extract_service_features()
        _extract_specialty_features()
        _extract_ratio_features()
        
    except Exception as e:
        print(f"Error extracting features: {str(e)}")
        raise

def _extract_provider_features():
    """Extract provider-related features"""
    # Feature 1: Ratio of total providers to unique providers
    providers_count_per_month = app_state.data.groupby(['year_month', 'ID']).agg(
        total_providers_monthly=('provider_name', 'count')
    ).reset_index()
    app_state.data = app_state.data.merge(providers_count_per_month, on=['year_month', 'ID'], how='left')
    
    unique_providers_per_month = app_state.data.groupby(['year_month', 'ID']).agg(
        unique_providers=('provider_name', 'nunique')
    ).reset_index()
    app_state.data = app_state.data.merge(unique_providers_per_month, on=['year_month', 'ID'], how='left')
    
    from utils import safe_division
    app_state.data['unq_ratio_provider'] = app_state.data.apply(
        lambda row: safe_division(row['total_providers_monthly'], row['unique_providers']), 
        axis=1
    )

def _extract_patient_features():
    """Extract patient-related features"""
    # Feature 2: Ratio of total patients to unique patients
    patients_count_per_month = app_state.data.groupby(['year_month', 'provider_name']).agg(
        total_patients_monthly=('ID', 'count')
    ).reset_index()
    app_state.data = app_state.data.merge(patients_count_per_month, on=['year_month', 'provider_name'], how='left')
    
    unique_patients_per_month = app_state.data.groupby(['year_month', 'provider_name']).agg(
        unique_patients=('ID', 'nunique')
    ).reset_index()
    app_state.data = app_state.data.merge(unique_patients_per_month, on=['year_month', 'provider_name'], how='left')
    
    from utils import safe_division
    app_state.data['unq_ratio_patient'] = app_state.data.apply(
        lambda row: safe_division(row['total_patients_monthly'], row['unique_patients']), 
        axis=1
    )
    
    # Feature 3 & 4: Provider and Patient cost change percentage
    _extract_cost_change_features()

def _extract_cost_change_features():
    """Extract cost change percentage features"""
    from utils import calculate_percentage_change
    
    # Provider cost change
    monthly_means = app_state.data.groupby(['year_month', 'provider_name']).agg(
        mean_amount_provider=('cost_amount', 'mean')
    ).reset_index()
    
    monthly_means['previous_mean_amount_provider_1'] = monthly_means.groupby('provider_name')['mean_amount_provider'].shift(1)
    monthly_means['previous_mean_amount_provider_2'] = monthly_means.groupby('provider_name')['mean_amount_provider'].shift(2)
    monthly_means['average_previous_mean_provider'] = monthly_means[['previous_mean_amount_provider_1', 'previous_mean_amount_provider_2']].mean(axis=1)
    
    monthly_means['percent_change_provider'] = monthly_means.apply(
        lambda row: calculate_percentage_change(
            row['mean_amount_provider'], 
            row['average_previous_mean_provider']
        ), 
        axis=1
    )
    
    app_state.data = app_state.data.merge(monthly_means, on=['year_month', 'provider_name'], how='left', suffixes=('', '_monthly'))
    
    # Patient cost change
    monthly_means = app_state.data.groupby(['year_month', 'ID']).agg(
        mean_amount_patient=('cost_amount', 'mean')
    ).reset_index()
    
    monthly_means['previous_mean_amount_patient_1'] = monthly_means.groupby('ID')['mean_amount_patient'].shift(1)
    monthly_means['previous_mean_amount_patient_2'] = monthly_means.groupby('ID')['mean_amount_patient'].shift(2)
    monthly_means['average_previous_mean_patient'] = monthly_means[['previous_mean_amount_patient_1', 'previous_mean_amount_patient_2']].mean(axis=1)
    
    monthly_means['percent_change_patient'] = monthly_means.apply(
        lambda row: calculate_percentage_change(
            row['mean_amount_patient'], 
            row['average_previous_mean_patient']
        ), 
        axis=1
    )
    
    app_state.data = app_state.data.merge(monthly_means, on=['year_month', 'ID'], how='left', suffixes=('', '_monthly'))

def _extract_service_features():
    """Extract service-related features"""
    # Feature 5: Service cost difference percentage
    monthly_avg = app_state.data.groupby(['year_month', 'Service']).agg(avg_amount=('cost_amount', 'mean')).reset_index()
    app_state.data = app_state.data.merge(monthly_avg, on=['year_month', 'Service'], how='left', suffixes=('', '_monthly'))
    app_state.data['percent_difference'] = ((app_state.data['cost_amount'] - app_state.data['avg_amount']) / app_state.data['avg_amount']) * 100
    app_state.data.loc[app_state.data['Service'] == 'دارو و ملزومات دارویی', 'percent_difference'] = 0
    app_state.data['percent_difference'] = app_state.data['percent_difference'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
    
    # Feature 6: Service cost change for provider
    monthly_avg_per_provider = app_state.data.groupby(['year_month', 'provider_name', 'Service']).agg(
        avg_amount_ser=('cost_amount', 'mean')
    ).reset_index()
    
    monthly_avg_overall = app_state.data.groupby(['year_month', 'Service']).agg(
        overall_avg_amount_ser=('cost_amount', 'mean')
    ).reset_index()
    
    monthly_avg_overall['prev_avg_amount_serv'] = monthly_avg_overall.groupby('Service')['overall_avg_amount_ser'].shift(1)
    app_state.data = app_state.data.merge(monthly_avg_per_provider[['year_month', 'provider_name', 'Service', 'avg_amount_ser']], 
                     on=['year_month', 'provider_name', 'Service'], how='left', suffixes=('', '_provider'))
    app_state.data = app_state.data.merge(monthly_avg_overall[['year_month', 'Service', 'prev_avg_amount_serv']], 
                     on=['year_month', 'Service'], how='left')
    app_state.data['percent_diff_ser'] = ((app_state.data['avg_amount_ser'] - app_state.data['prev_avg_amount_serv']) / app_state.data['prev_avg_amount_serv']) * 100
    app_state.data.loc[app_state.data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_ser'] = 0
    app_state.data['percent_diff_ser'] = app_state.data['percent_diff_ser'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
    
    # Feature 8.1: Service cost change for patient
    monthly_avg_per_patient = app_state.data.groupby(['year_month', 'ID', 'Service']).agg(
        avg_amount_ser_patient=('cost_amount', 'mean')
    ).reset_index()
    
    monthly_avg_overall_patient = app_state.data.groupby(['year_month', 'Service']).agg(
        overall_avg_amount_ser_patient=('cost_amount', 'mean')
    ).reset_index()
    
    monthly_avg_overall_patient['prev_avg_amount_serv_patient'] = monthly_avg_overall_patient.groupby('Service')['overall_avg_amount_ser_patient'].shift(1)
    app_state.data = app_state.data.merge(monthly_avg_per_patient[['year_month', 'ID', 'Service', 'avg_amount_ser_patient']], 
                     on=['year_month', 'ID', 'Service'], how='left', suffixes=('', '_patient'))
    app_state.data = app_state.data.merge(monthly_avg_overall_patient[['year_month', 'Service', 'prev_avg_amount_serv_patient']], 
                     on=['year_month', 'Service'], how='left')
    app_state.data['percent_diff_ser_patient'] = ((app_state.data['avg_amount_ser_patient'] - app_state.data['prev_avg_amount_serv_patient']) / app_state.data['prev_avg_amount_serv_patient']) * 100
    app_state.data.loc[app_state.data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_ser_patient'] = 0
    app_state.data['percent_diff_ser_patient'] = app_state.data['percent_diff_ser_patient'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
    
    # Feature 8.2: Service cost change (overall)
    monthly_avg_overall = app_state.data.groupby(['year_month', 'Service']).agg(
        overall_avg_amount_ser=('cost_amount', 'mean')
    ).reset_index()
    
    monthly_avg_overall['prev_avg_amount_ser'] = monthly_avg_overall.groupby('Service')['overall_avg_amount_ser'].shift(1)
    app_state.data = app_state.data.merge(monthly_avg_overall[['year_month', 'Service', 'prev_avg_amount_ser']], 
                     on=['year_month', 'Service'], how='left')
    app_state.data['percent_diff_serv'] = ((app_state.data['cost_amount'] - app_state.data['prev_avg_amount_ser']) / app_state.data['prev_avg_amount_ser']) * 100
    app_state.data.loc[app_state.data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_serv'] = 0
    app_state.data['percent_diff_serv'] = app_state.data['percent_diff_serv'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)

def _extract_specialty_features():
    """Extract specialty-related features"""
    # Feature 7: Specialty cost change for provider
    monthly_avg_per_provider_spe = app_state.data.groupby(['year_month', 'provider_name', 'provider_specialty']).agg(
        avg_amount_spe=('cost_amount', 'mean')
    ).reset_index()
    
    monthly_avg_overall_spe = app_state.data.groupby(['year_month', 'provider_specialty']).agg(
        overall_avg_amount_spe=('cost_amount', 'mean')
    ).reset_index()
    
    monthly_avg_overall_spe['prev_avg_amount_spe'] = monthly_avg_overall_spe.groupby('provider_specialty')['overall_avg_amount_spe'].shift(1)
    app_state.data = app_state.data.merge(monthly_avg_per_provider_spe[['year_month', 'provider_name', 'provider_specialty', 'avg_amount_spe']], 
                     on=['year_month', 'provider_name', 'provider_specialty'], how='left', suffixes=('', '_provider'))
    app_state.data = app_state.data.merge(monthly_avg_overall_spe[['year_month', 'provider_specialty', 'prev_avg_amount_spe']], 
                     on=['year_month', 'provider_specialty'], how='left')
    app_state.data['percent_diff_spe'] = ((app_state.data['avg_amount_spe'] - app_state.data['prev_avg_amount_spe']) / app_state.data['prev_avg_amount_spe']) * 100
    app_state.data['percent_diff_spe'] = app_state.data['percent_diff_spe'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
    
    # Feature 7.2: Specialty cost change for provider (direct)
    app_state.data['percent_diff_spe2'] = ((app_state.data['cost_amount'] - app_state.data['prev_avg_amount_spe']) / app_state.data['prev_avg_amount_spe']) * 100
    app_state.data['percent_diff_spe2'] = app_state.data['percent_diff_spe2'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)

def _extract_ratio_features():
    """Extract ratio-related features"""
    # Feature 9: Service ratio
    provider_service_count = app_state.data.groupby(['provider_name', 'Service']).size().reset_index(name='Count')
    
    provider_count = app_state.data['provider_name'].value_counts().reset_index()
    provider_count.columns = ['provider_name', 'TotalCount']
    
    merged = pd.merge(provider_service_count, provider_count, on='provider_name')
    merged['Ratio'] = 1 - (merged['Count'] / merged['TotalCount'])
    merged.loc[merged['TotalCount'] == 1, 'Ratio'] = 0
    app_state.data = pd.merge(app_state.data, merged[['provider_name', 'Service', 'Ratio']], 
                   on=['provider_name', 'Service'], how='left')

def train_model():
    """Train the Isolation Forest model"""
    # Select features
    features = ['unq_ratio_provider', 'unq_ratio_patient', 'percent_change_provider', 
                'percent_change_patient', 'percent_difference', 'percent_diff_ser', 
                'percent_diff_spe', 'percent_diff_spe2', 'percent_diff_ser_patient', 
                'percent_diff_serv', 'Ratio']
    
    # Create final dataset with features (preserve indices for alignment)
    app_state.data_final = app_state.data[features].copy()
    app_state.data_final.dropna(inplace=True)
    
    # Standardize features
    app_state.scaler = StandardScaler()
    X = app_state.scaler.fit_transform(app_state.data_final)
    
    # Train Isolation Forest
    app_state.clf = IsolationForest(
        n_estimators=200,
        max_samples=36000,
        max_features=4,
        contamination=0.2,
        random_state=42
    )
    app_state.clf.fit(X)

    # Predict on training data and enrich data_final with metadata used by charts
    y_pred = app_state.clf.predict(X)
    app_state.data_final['prediction'] = y_pred

    # Attach metadata columns aligned by original indices
    _attach_metadata_columns()

def _attach_metadata_columns():
    """Attach metadata columns to data_final for chart generation"""
    meta_columns = [
        'Adm_date', 'gender', 'age', 'Service', 'province',
        'Ins_Cover', 'Invice-type', 'Type_Medical_Record',
        'provider_name', 'ID'
    ]
    for col in meta_columns:
        if col in app_state.data.columns:
            app_state.data_final[col] = app_state.data.loc[app_state.data_final.index, col]

def predict_new_prescription(prescription_data):
    """Predict fraud for a new prescription"""
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
    data1 = app_state.data[features1].copy()
    
    # Calculate features using helper function
    _calculate_all_features(data1, new_sample)
    
    # Select features for prediction
    features = ['unq_ratio_provider', 'unq_ratio_patient', 'percent_change_provider', 
                'percent_change_patient', 'percent_difference', 'percent_diff_ser', 
                'percent_diff_spe', 'percent_diff_spe2', 'percent_diff_ser_patient', 
                'percent_diff_serv', 'Ratio']
    
    new_sample_final = new_sample[features].copy()
    
    # Normalize features
    full_data = pd.concat([app_state.data_final, new_sample_final], ignore_index=True)
    scaler_temp = StandardScaler()
    scaler_temp.fit(full_data)
    normalized_array = scaler_temp.transform(new_sample_final)
    
    # Predict
    y_new_pred = app_state.clf.predict(normalized_array)
    scores_new = app_state.clf.decision_function(normalized_array)
    
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

def _calculate_all_features(data1, new_sample):
    """Calculate all features for the new sample"""
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

def create_chart(chart_type, **kwargs):
    """Create various charts and return as base64 string"""
    plt.figure(figsize=(12, 6))
    
    if chart_type == 'risk_indicators':
        risk_indices = ['unq_ratio_provider', 'unq_ratio_patient', 'percent_change_provider',
                       'percent_change_patient', 'percent_difference', 'percent_diff_ser',
                       'percent_diff_spe', 'percent_diff_spe2', 'percent_diff_ser_patient',
                       'percent_diff_serv', 'Ratio']
        risk_values = kwargs.get('risk_values', [])
        plt.bar(risk_indices, risk_values, color='skyblue')
        plt.xlabel('شاخص‌های ریسک')
        plt.ylabel('مقدار شاخص ریسک (0 تا 100)')
        plt.title('مقدار هر یک از شاخص‌های ریسک نسخه پزشکی')
        plt.xticks(rotation=45)
    
    elif chart_type == 'fraud_by_province':
        fraud_data = app_state.data_final[app_state.data_final['prediction'] == -1]
        fraud_counts_by_province = fraud_data['province'].value_counts()
        fraud_counts_by_province.plot(kind='bar')
        plt.xlabel('استان')
        plt.ylabel('تعداد نسخه‌های تقلبی')
        plt.title('تعداد نسخه‌های تقلبی بر اساس استان‌ها')
        plt.xticks(rotation=45)
    
    elif chart_type == 'fraud_by_gender':
        counts = app_state.data_final.groupby(['gender', 'prediction']).size().unstack(fill_value=0)
        if 1 not in counts.columns:
            counts[1] = 0
        if -1 not in counts.columns:
            counts[-1] = 0
        ratios = counts.apply(
            lambda row: row[-1] / (row[1] + row[-1]) if (row[1] + row[-1]) != 0 else 0, axis=1
        )
        plt.pie(ratios, labels=ratios.index, autopct='%.2f%%', startangle=90)
        plt.title('نسبت نسخه‌های تقلبی به کل نسخه ها بر اساس جنسیت')
    
    elif chart_type == 'fraud_by_age_group':
        bins = [0, 4, 12, 19, 34, 49, 64, 100]
        labels = ['نوزادان', 'کودکان', 'نوجوانان', 'جوانان', 'بزرگسالان', 'میانسالان', 'سالمندان']
        app_state.data_final['age_group'] = pd.cut(app_state.data_final['age'], bins=bins, labels=labels, right=True)
        counts = app_state.data_final.groupby(['age_group', 'prediction']).size().unstack(fill_value=0)
        if 1 not in counts.columns:
            counts[1] = 0
        if -1 not in counts.columns:
            counts[-1] = 0
        ratios = counts.apply(
            lambda row: row[-1] / (row[1] + row[-1]) if (row[1] + row[-1]) != 0 else 0, axis=1
        )
        plt.pie(ratios, labels=ratios.index, autopct='%.2f%%', startangle=90)
        plt.title('نسبت نسخه‌های تقلبی به نرمال بر اساس گروه سنی')

    elif chart_type == 'fraud_ratio_by_age_group':
        _create_fraud_ratio_by_age_group_chart()
    elif chart_type == 'province_fraud_ratio':
        _create_province_fraud_ratio_chart()

    elif chart_type == 'province_gender_fraud_percentage':
        total_counts = app_state.data_final.groupby(['province', 'gender']).size().unstack(fill_value=0)
        fraud_counts = app_state.data_final[app_state.data_final['prediction'] == -1].groupby(['province', 'gender']).size().unstack(fill_value=0)
        percentage_fraud = (fraud_counts / total_counts * 100).fillna(0)
        percentage_fraud.plot(kind='bar')
        plt.title('درصد نسخه‌های تقلبی در هر استان بر حسب جنسیت')
        plt.xlabel('استان‌ها')
        plt.ylabel('درصد نسخه‌های تقلبی (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()

    elif chart_type == 'fraud_counts_by_date':
        df = app_state.data_final.copy()
        df['Adm_date'] = pd.to_datetime(df['Adm_date'])
        fraud_by_date = df[df['prediction'] == -1].groupby('Adm_date').size()
        ax = fraud_by_date.plot()
        ax.set_xlabel('تاریخ پذیرش نسخه')
        ax.set_ylabel('تعداد نسخه تقلبی')
        ax.set_title('تعداد نسخه‌های تقلبی بر حسب تاریخ پذیرش')
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.grid(True)

    elif chart_type == 'fraud_ratio_by_date':
        df = app_state.data_final.copy()
        df['Adm_date'] = pd.to_datetime(df['Adm_date'])
        fraud_counts = df[df['prediction'] == -1].groupby('Adm_date').size()
        total_counts = df.groupby('Adm_date').size()
        fraud_ratio = (fraud_counts / total_counts).fillna(0)
        ax = fraud_ratio.plot()
        ax.set_xlabel('تاریخ پذیرش نسخه')
        ax.set_ylabel('نسبت نسخه تقلبی به کل نسخه‌ها')
        ax.set_title('نسبت نسخه‌های تقلبی بر حسب تاریخ پذیرش')
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.grid(True)

    elif chart_type == 'fraud_ratio_by_ins_cover':
        counts = app_state.data_final.groupby(['Ins_Cover', 'prediction']).size().unstack(fill_value=0)
        ratio = _calculate_fraud_ratio(counts)
        ratio.sort_values().plot(kind='bar')
        plt.xlabel('نوع پوشش')
        plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
        plt.title('نسبت نسخه‌های تقلبی به کل در هر پوشش')
        plt.xticks(rotation=45)

    elif chart_type == 'fraud_ratio_by_invoice_type':
        col = 'Invice-type'
        counts = app_state.data_final.groupby([col, 'prediction']).size().unstack(fill_value=0)
        ratio = _calculate_fraud_ratio(counts)
        ratio.sort_values().plot(kind='bar')
        plt.xlabel('نوع پوشش')
        plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
        plt.title('نسبت نسخه‌های تقلبی به کل در هر پوشش')
        plt.xticks(rotation=45)

    elif chart_type == 'fraud_ratio_by_medical_record_type':
        col = 'Type_Medical_Record'
        counts = app_state.data_final.groupby([col, 'prediction']).size().unstack(fill_value=0)
        ratio = _calculate_fraud_ratio(counts)
        ratio.sort_values().plot(kind='bar')
        plt.xlabel('نوع پرونده پزشکی')
        plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
        plt.title('نسبت نسخه‌های تقلبی به کل در هر نوع پرونده')
        plt.xticks(rotation=45)

    elif chart_type == 'provider_risk_indicator_time_series':
        provider_name = kwargs.get('provider_name')
        indicator = kwargs.get('indicator')
        if provider_name is None or indicator is None:
            raise ValueError('provider_name and indicator are required')
        df = app_state.data_final.copy()
        if indicator not in df.columns:
            raise ValueError(f'Indicator {indicator} not found')
        # compute z-score then CDF (0-100)
        from scipy.stats import zscore, norm
        df['risk_value'] = norm.cdf(zscore(df[indicator].astype(float))) * 100
        df['Adm_date'] = pd.to_datetime(df['Adm_date'])
        df = df[df['provider_name'] == provider_name].sort_values('Adm_date')
        import seaborn as sns
        sns.lineplot(data=df, x='Adm_date', y='risk_value', marker='o')
        plt.title(f'شاخص ریسک {indicator} برای پزشک {provider_name}')
        plt.xlabel('تاریخ نسخه')
        plt.ylabel('شاخص ریسک (0-100)')
        plt.xticks(rotation=45)

    elif chart_type == 'patient_risk_indicator_time_series':
        patient_id = kwargs.get('patient_id')
        indicator = kwargs.get('indicator')
        if patient_id is None or indicator is None:
            raise ValueError('patient_id and indicator are required')
        df = app_state.data_final.copy()
        if indicator not in df.columns:
            raise ValueError(f'Indicator {indicator} not found')
        from scipy.stats import zscore, norm
        df['risk_value'] = norm.cdf(zscore(df[indicator].astype(float))) * 100
        df['Adm_date'] = pd.to_datetime(df['Adm_date'])
        df = df[df['ID'] == int(patient_id)].sort_values('Adm_date')
        import seaborn as sns
        sns.lineplot(data=df, x='Adm_date', y='risk_value', marker='o')
        plt.title(f'شاخص ریسک {indicator} برای بیمار {patient_id}')
        plt.xlabel('تاریخ نسخه')
        plt.ylabel('شاخص ریسک (0-100)')
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # Convert plot to base64 string
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=300)
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode()

def _create_fraud_ratio_by_age_group_chart():
    """Create fraud ratio by age group bar chart"""
    bins = [0, 4, 12, 19, 34, 49, 64, 100]
    labels = ['نوزادان', 'کودکان', 'نوجوانان', 'جوانان', 'بزرگسالان', 'میانسالان', 'سالمندان']
    app_state.data_final['age_group'] = pd.cut(app_state.data_final['age'], bins=bins, labels=labels, right=True)
    counts = app_state.data_final.groupby(['age_group', 'prediction']).size().unstack(fill_value=0)
    ratio = _calculate_fraud_ratio(counts)
    ratio.sort_values().plot(kind='bar')
    plt.xlabel('گروه سنی')
    plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
    plt.title('نسبت نسخه‌های تقلبی به کل در هر گروه سنی')
    plt.xticks(rotation=45)

def _create_province_fraud_ratio_chart():
    """Create province fraud ratio bar chart"""
    counts = app_state.data_final.groupby(['province', 'prediction']).size().unstack(fill_value=0)
    fraud_ratio = _calculate_fraud_ratio(counts)
    fraud_ratio.sort_values(ascending=True).plot(kind='bar')
    plt.xlabel('استان')
    plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
    plt.title('نسبت نسخه‌های تقلبی به کل در هر استان')
    plt.xticks(rotation=45)

def _calculate_fraud_ratio(counts):
    """Calculate fraud ratio from prediction counts"""
    if 1 not in counts.columns:
        counts[1] = 0
    if -1 not in counts.columns:
        counts[-1] = 0
    return (counts[-1] / (counts[1] + counts[-1])).dropna()

@app.route('/')
def home():
    """Home page with API documentation"""
    html = """
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API تشخیص تقلب پزشکی</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .endpoint { background: #ecf0f1; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #3498db; }
            .method { background: #e74c3c; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
            .url { background: #2c3e50; color: white; padding: 5px 10px; border-radius: 3px; font-family: monospace; }
            pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
            .example { background: #d5f4e6; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 API تشخیص تقلب پزشکی</h1>
            
            <div class="warning">
                <strong>⚠️ توجه:</strong> این API برای تشخیص تقلب در نسخه‌های پزشکی طراحی شده است.
            </div>
            
            <h2>📋 نقاط پایانی (Endpoints)</h2>
            
            <div class="endpoint">
                <span class="method">POST</span>
                <span class="url">/predict</span>
                <p><strong>تشخیص تقلب برای یک نسخه جدید</strong></p>
                <p>این نقطه پایانی اطلاعات یک نسخه پزشکی را دریافت کرده و احتمال تقلب بودن آن را محاسبه می‌کند.</p>
                
                <h4>پارامترهای ورودی:</h4>
                <pre>{
    "ID": 48928,
    "jalali_date": "1361/05/04",
    "Adm_date": "1403/08/05",
    "Service": "ویزیت متخصص",
    "provider_name": "حسینخان خسروخاور",
    "provider_specialty": "دکترای حرفه‌ای پزشکی",
    "cost_amount": 2000000
}</pre>
                
                <h4>پاسخ:</h4>
                <pre>{
    "prediction": 1,
    "score": 0.038,
    "is_fraud": false,
    "risk_scores": [26.97, 52.54, 37.94, ...],
    "features": {...}
}</pre>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="url">/charts/fraud-by-province</span>
                <p><strong>نمودار تقلب بر اساس استان</strong></p>
                <p>نمودار میله‌ای از تعداد نسخه‌های تقلبی در هر استان.</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="url">/charts/fraud-by-gender</span>
                <p><strong>نمودار تقلب بر اساس جنسیت</strong></p>
                <p>نمودار دایره‌ای از نسبت نسخه‌های تقلبی بر اساس جنسیت.</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="url">/charts/fraud-by-age</span>
                <p><strong>نمودار تقلب بر اساس گروه سنی</strong></p>
                <p>نمودار دایره‌ای از نسبت نسخه‌های تقلبی بر اساس گروه سنی.</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="url">/stats</span>
                <p><strong>آمار کلی سیستم</strong></p>
                <p>آمار کلی از داده‌های موجود و نتایج تشخیص تقلب.</p>
            </div>
            
            <h2>🔧 نحوه استفاده</h2>
            <div class="example">
                <h4>مثال با cURL:</h4>
                <pre>curl -X POST http://localhost:5000/predict \\
     -H "Content-Type: application/json" \\
     -d '{
         "ID": 48928,
         "jalali_date": "1361/05/04",
         "Adm_date": "1403/08/05",
         "Service": "ویزیت متخصص",
         "provider_name": "حسینخان خسروخاور",
         "provider_specialty": "دکترای حرفه‌ای پزشکی",
         "cost_amount": 2000000
     }'</pre>
            </div>
            
            <h2>📊 ویژگی‌های سیستم</h2>
            <ul>
                <li>تشخیص تقلب با الگوریتم Isolation Forest</li>
                <li>محاسبه ۱۱ شاخص ریسک مختلف</li>
                <li>نمودارهای تحلیلی متنوع</li>
                <li>پشتیبانی از تاریخ شمسی</li>
                <li>محاسبه سن بر اساس تاریخ تولد</li>
                <li>تحلیل بر اساس استان، جنسیت و گروه سنی</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/predict', methods=['POST'])
def predict():
    """Predict fraud for a new prescription
    ---
    tags:
      - Predictions
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [ID, jalali_date, Adm_date, Service, provider_name, provider_specialty, cost_amount]
          properties:
            ID:
              type: integer
              example: 48928
            jalali_date:
              type: string
              description: Jalali date of birth in YYYY/MM/DD
              example: "1361/05/04"
            Adm_date:
              type: string
              description: Jalali admission date in YYYY/MM/DD
              example: "1403/08/05"
            Service:
              type: string
              example: "ویزیت متخصص"
            provider_name:
              type: string
              example: "حسینخان خسروخاور"
            provider_specialty:
              type: string
              example: "دکترای حرفه‌ای پزشکی"
            cost_amount:
              type: number
              example: 2000000
    responses:
      200:
        description: Prediction result
        schema:
          type: object
          properties:
            prediction:
              type: integer
              enum: [-1, 1]
            score:
              type: number
            is_fraud:
              type: boolean
            risk_scores:
              type: array
              items:
                type: number
            features:
              type: object
      400:
        description: Validation error
      500:
        description: Server error
    """
    try:
        prescription_data = request.json
        
        # Validate required fields
        required_fields = ['ID', 'jalali_date', 'Adm_date', 'Service', 'provider_name', 'provider_specialty', 'cost_amount']
        for field in required_fields:
            if field not in prescription_data:
                return jsonify({'error': f'فیلد {field} الزامی است'}), 400
        
        # Make prediction
        result = predict_new_prescription(prescription_data)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/charts/fraud-by-province')
def fraud_by_province_chart():
    """Generate fraud by province chart
    ---
    tags:
      - Charts
    produces:
      - application/json
    responses:
      200:
        description: Base64-encoded PNG chart
        schema:
          type: object
          properties:
            chart:
              type: string
              description: Base64 PNG image string
      500:
        description: Server error
    """
    try:
        chart_data = create_chart('fraud_by_province')
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/charts/fraud-by-gender')
def fraud_by_gender_chart():
    """Generate fraud by gender chart
    ---
    tags:
      - Charts
    produces:
      - application/json
    responses:
      200:
        description: Base64-encoded PNG chart
        schema:
          type: object
          properties:
            chart:
              type: string
              description: Base64 PNG image string
      500:
        description: Server error
    """
    try:
        chart_data = create_chart('fraud_by_gender')
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/charts/fraud-by-age')
def fraud_by_age_chart():
    """Generate fraud by age group chart
    ---
    tags:
      - Charts
    produces:
      - application/json
    responses:
      200:
        description: Base64-encoded PNG chart
        schema:
          type: object
          properties:
            chart:
              type: string
              description: Base64 PNG image string
      500:
        description: Server error
    """
    try:
        chart_data = create_chart('fraud_by_age_group')
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/charts/risk-indicators', methods=['POST'])
def risk_indicators_chart():
    """Generate risk indicators chart for a prescription
    ---
    tags:
      - Charts
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [ID, jalali_date, Adm_date, Service, provider_name, provider_specialty, cost_amount]
          properties:
            ID:
              type: integer
            jalali_date:
              type: string
            Adm_date:
              type: string
            Service:
              type: string
            provider_name:
              type: string
            provider_specialty:
              type: string
            cost_amount:
              type: number
    responses:
      200:
        description: Chart and prediction
        schema:
          type: object
          properties:
            chart:
              type: string
            prediction:
              type: object
      500:
        description: Server error
    """
    try:
        prescription_data = request.json
        result = predict_new_prescription(prescription_data)
        chart_data = create_chart('risk_indicators', risk_values=result['risk_scores'])
        return jsonify({'chart': chart_data, 'prediction': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/charts/fraud-ratio-by-age-group')
def fraud_ratio_by_age_group_chart():
    """Fraud ratio by age group
    ---
    tags:
      - Charts
    responses:
      200:
        description: Base64-encoded PNG chart
    """
    try:
        chart_data = create_chart('fraud_ratio_by_age_group')
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def get_stats():
    """Get system statistics
    ---
    tags:
      - System
    produces:
      - application/json
    responses:
      200:
        description: Overall statistics
        schema:
          type: object
          properties:
            total_prescriptions:
              type: integer
            fraud_prescriptions:
              type: integer
            normal_prescriptions:
              type: integer
            fraud_percentage:
              type: number
            model_contamination:
              type: number
            features_count:
              type: integer
      500:
        description: Server error
    """
    try:
        if app_state.data_final is None:
            return jsonify({'error': 'داده‌ها بارگذاری نشده‌اند'}), 500
        
        total_prescriptions = len(app_state.data_final)
        fraud_prescriptions = len(app_state.data_final[app_state.data_final['prediction'] == -1])
        normal_prescriptions = len(app_state.data_final[app_state.data_final['prediction'] == 1])
        fraud_percentage = (fraud_prescriptions / total_prescriptions) * 100
        
        stats = {
            'total_prescriptions': total_prescriptions,
            'fraud_prescriptions': fraud_prescriptions,
            'normal_prescriptions': normal_prescriptions,
            'fraud_percentage': round(fraud_percentage, 2),
            'model_contamination': 0.2,
            'features_count': 11
        }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint
    ---
    tags:
      - System
    produces:
      - application/json
    responses:
      200:
        description: Health status
        schema:
          type: object
          properties:
            status:
              type: string
            model_loaded:
              type: boolean
            data_loaded:
              type: boolean
            timestamp:
              type: string
              format: date-time
    """
    return jsonify({
        'status': 'healthy',
        'model_loaded': app_state.clf is not None,
        'data_loaded': app_state.data is not None,
        'timestamp': datetime.now().isoformat()
    })

# Additional chart endpoints mapped from notebook analyses
@app.route('/charts/province-fraud-ratio')
def province_fraud_ratio_chart():
    """Fraud ratio per province
    ---
    tags:
      - Charts
    responses:
      200:
        description: Base64-encoded PNG chart
    """
    try:
        chart_data = create_chart('province_fraud_ratio')
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/charts/province-gender-fraud-percentage')
def province_gender_fraud_percentage_chart():
    """Fraud percentage by province and gender
    ---
    tags:
      - Charts
    responses:
      200:
        description: Base64-encoded PNG chart
    """
    try:
        chart_data = create_chart('province_gender_fraud_percentage')
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/charts/fraud-counts-by-date')
def fraud_counts_by_date_chart():
    """Fraud counts over time (by admission date)
    ---
    tags:
      - Charts
    responses:
      200:
        description: Base64-encoded PNG chart
    """
    try:
        chart_data = create_chart('fraud_counts_by_date')
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/charts/fraud-ratio-by-date')
def fraud_ratio_by_date_chart():
    """Fraud ratio over time (by admission date)
    ---
    tags:
      - Charts
    responses:
      200:
        description: Base64-encoded PNG chart
    """
    try:
        chart_data = create_chart('fraud_ratio_by_date')
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/charts/fraud-ratio-by-ins-cover')
def fraud_ratio_by_ins_cover_chart():
    """Fraud ratio by insurance cover
    ---
    tags:
      - Charts
    responses:
      200:
        description: Base64-encoded PNG chart
    """
    try:
        chart_data = create_chart('fraud_ratio_by_ins_cover')
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/charts/fraud-ratio-by-invoice-type')
def fraud_ratio_by_invoice_type_chart():
    """Fraud ratio by invoice type
    ---
    tags:
      - Charts
    responses:
      200:
        description: Base64-encoded PNG chart
    """
    try:
        chart_data = create_chart('fraud_ratio_by_invoice_type')
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/charts/fraud-ratio-by-medical-record-type')
def fraud_ratio_by_medical_record_type_chart():
    """Fraud ratio by medical record type
    ---
    tags:
      - Charts
    responses:
      200:
        description: Base64-encoded PNG chart
    """
    try:
        chart_data = create_chart('fraud_ratio_by_medical_record_type')
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/charts/provider-risk-indicator', methods=['GET'])
def provider_risk_indicator_chart():
    """Provider risk indicator over time
    ---
    tags:
      - Charts
    parameters:
      - in: query
        name: provider_name
        type: string
        required: true
      - in: query
        name: indicator
        type: string
        required: true
    responses:
      200:
        description: Base64-encoded PNG chart
    """
    try:
        provider_name = request.args.get('provider_name')
        indicator = request.args.get('indicator')
        chart_data = create_chart('provider_risk_indicator_time_series', provider_name=provider_name, indicator=indicator)
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/charts/patient-risk-indicator', methods=['GET'])
def patient_risk_indicator_chart():
    """Patient risk indicator over time
    ---
    tags:
      - Charts
    parameters:
      - in: query
        name: patient_id
        type: integer
        required: true
      - in: query
        name: indicator
        type: string
        required: true
    responses:
      200:
        description: Base64-encoded PNG chart
    """
    try:
        patient_id = request.args.get('patient_id')
        indicator = request.args.get('indicator')
        chart_data = create_chart('patient_risk_indicator_time_series', patient_id=patient_id, indicator=indicator)
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Loading data and training model...")
    load_and_prepare_data()
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
