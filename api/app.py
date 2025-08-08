from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from flasgger import Swagger
import pandas as pd
import numpy as np
import warnings
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import json
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from scipy.stats import norm
import arabic_reshaper
from bidi.algorithm import get_display
from matplotlib import font_manager, rc
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

warnings.filterwarnings('ignore')
pd.set_option('display.max_column', 50)
pd.set_option('display.max_rows', 100)

app = Flask(__name__)
CORS(app)

# Initialize Swagger (OpenAPI) UI at /docs
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

# Swagger UI configuration
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

# Global variables for model and data
data = None
clf = None
scaler = None
data_final = None

def load_and_prepare_data():
    """Load and prepare the dataset"""
    global data, clf, scaler, data_final
    
    print("Loading dataset...")
    data = pd.read_csv('DataSEt_FD7.csv')
    
    # Remove commas and spaces
    data['cost_amount'] = data['cost_amount'].str.replace(',', '').str.strip()
    data['ded_amount'] = data['ded_amount'].str.replace(',', '').str.strip()
    data['confirmed_amount'] = data['confirmed_amount'].str.replace(',', '').str.strip()
    
    # Convert to numeric
    data['cost_amount'] = pd.to_numeric(data['cost_amount'], errors='coerce').fillna(0).astype(int)
    data['ded_amount'] = pd.to_numeric(data['ded_amount'], errors='coerce').fillna(0).astype(int)
    data['confirmed_amount'] = pd.to_numeric(data['confirmed_amount'], errors='coerce').fillna(0).astype(int)
    
    # Fill missing provider names
    data['provider_name'] = data['provider_name'].fillna(data['Ref_code'])
    data['provider_name'] = data['provider_name'].fillna(data['Ref_name'])
    
    # Load specialties
    specialties = pd.read_csv('specialties.csv')
    merged_data = data.merge(specialties, on='Service', how='left')
    data['provider_specialty'] = data['provider_specialty'].combine_first(merged_data['specialty'])
    
    # Add age column
    data['age'] = data['jalali_date'].apply(calculate_age)
    
    # Convert dates
    data['Adm_date'] = data['Adm_date'].apply(shamsi_to_miladi)
    data['confirm_date'] = data['confirm_date'].apply(shamsi_to_miladi)
    data['confirm_date'] = data['confirm_date'].fillna(data['Adm_date'].apply(add_one_month))
    
    # Reset confirmed amount
    data['confirmed_amount'] = data['confirmed_amount'].fillna(0)
    data['record_id'] = range(1, len(data) + 1)
    data['Adm_date'] = pd.to_datetime(data['Adm_date'])
    data['year_month'] = data['Adm_date'].dt.to_period('M')
    
    print("Extracting features...")
    extract_features()
    
    print("Training model...")
    train_model()
    
    print("Data and model loaded successfully!")

def extract_features():
    """Extract all features from the dataset"""
    global data
    
    # Feature 1: Ratio of total providers to unique providers
    providers_count_per_month = data.groupby(['year_month', 'ID']).agg(
        total_providers_monthly=('provider_name', 'count')
    ).reset_index()
    data = data.merge(providers_count_per_month, on=['year_month', 'ID'], how='left')
    
    unique_providers_per_month = data.groupby(['year_month', 'ID']).agg(
        unique_providers=('provider_name', 'nunique')
    ).reset_index()
    data = data.merge(unique_providers_per_month, on=['year_month', 'ID'], how='left')
    data['unq_ratio_provider'] = data['total_providers_monthly'] / data['unique_providers']
    
    # Feature 2: Ratio of total patients to unique patients
    patients_count_per_month = data.groupby(['year_month', 'provider_name']).agg(
        total_patients_monthly=('ID', 'count')
    ).reset_index()
    data = data.merge(patients_count_per_month, on=['year_month', 'provider_name'], how='left')
    
    unique_patients_per_month = data.groupby(['year_month', 'provider_name']).agg(
        unique_patients=('ID', 'nunique')
    ).reset_index()
    data = data.merge(unique_patients_per_month, on=['year_month', 'provider_name'], how='left')
    data['unq_ratio_patient'] = data['total_patients_monthly'] / data['unique_patients']
    
    # Feature 3: Provider cost change percentage
    monthly_means = data.groupby(['year_month', 'provider_name']).agg(
        mean_amount_provider=('cost_amount', 'mean')
    ).reset_index()
    monthly_means['previous_mean_amount_provider_1'] = monthly_means.groupby('provider_name')['mean_amount_provider'].shift(1)
    monthly_means['previous_mean_amount_provider_2'] = monthly_means.groupby('provider_name')['mean_amount_provider'].shift(2)
    monthly_means['average_previous_mean_provider'] = monthly_means[['previous_mean_amount_provider_1', 'previous_mean_amount_provider_2']].mean(axis=1)
    monthly_means['percent_change_provider'] = ((monthly_means['mean_amount_provider'] - monthly_means['average_previous_mean_provider']) / monthly_means['average_previous_mean_provider']) * 100
    data = data.merge(monthly_means, on=['year_month', 'provider_name'], how='left', suffixes=('', '_monthly'))
    data['percent_change_provider'] = data['percent_change_provider'].apply(lambda x: 0 if (pd.isna(x) or x < 0 or x > 2000) else x)
    
    # Feature 4: Patient cost change percentage
    monthly_means = data.groupby(['year_month', 'ID']).agg(
        mean_amount_patient=('cost_amount', 'mean')
    ).reset_index()
    monthly_means['previous_mean_amount_patient_1'] = monthly_means.groupby('ID')['mean_amount_patient'].shift(1)
    monthly_means['previous_mean_amount_patient_2'] = monthly_means.groupby('ID')['mean_amount_patient'].shift(2)
    monthly_means['average_previous_mean_patient'] = monthly_means[['previous_mean_amount_patient_1', 'previous_mean_amount_patient_2']].mean(axis=1)
    monthly_means['percent_change_patient'] = ((monthly_means['mean_amount_patient'] - monthly_means['average_previous_mean_patient']) / monthly_means['average_previous_mean_patient']) * 100
    data = data.merge(monthly_means, on=['year_month', 'ID'], how='left', suffixes=('', '_monthly'))
    data['percent_change_patient'] = data['percent_change_patient'].apply(lambda x: 0 if (pd.isna(x) or x < 0 or x > 2000) else x)
    
    # Feature 5: Service cost difference percentage
    monthly_avg = data.groupby(['year_month', 'Service']).agg(avg_amount=('cost_amount', 'mean')).reset_index()
    data = data.merge(monthly_avg, on=['year_month', 'Service'], how='left', suffixes=('', '_monthly'))
    data['percent_difference'] = ((data['cost_amount'] - data['avg_amount']) / data['avg_amount']) * 100
    data.loc[data['Service'] == 'دارو و ملزومات دارویی', 'percent_difference'] = 0
    data['percent_difference'] = data['percent_difference'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
    
    # Feature 6: Service cost change for provider
    monthly_avg_per_provider = data.groupby(['year_month', 'provider_name', 'Service']).agg(
        avg_amount_ser=('cost_amount', 'mean')
    ).reset_index()
    monthly_avg_overall = data.groupby(['year_month', 'Service']).agg(
        overall_avg_amount_ser=('cost_amount', 'mean')
    ).reset_index()
    monthly_avg_overall['prev_avg_amount_serv'] = monthly_avg_overall.groupby('Service')['overall_avg_amount_ser'].shift(1)
    data = data.merge(monthly_avg_per_provider[['year_month', 'provider_name', 'Service', 'avg_amount_ser']], 
                     on=['year_month', 'provider_name', 'Service'], how='left', suffixes=('', '_provider'))
    data = data.merge(monthly_avg_overall[['year_month', 'Service', 'prev_avg_amount_serv']], 
                     on=['year_month', 'Service'], how='left')
    data['percent_diff_ser'] = ((data['avg_amount_ser'] - data['prev_avg_amount_serv']) / data['prev_avg_amount_serv']) * 100
    data.loc[data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_ser'] = 0
    data['percent_diff_ser'] = data['percent_diff_ser'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
    
    # Feature 7: Specialty cost change for provider
    monthly_avg_per_provider_spe = data.groupby(['year_month', 'provider_name', 'provider_specialty']).agg(
        avg_amount_spe=('cost_amount', 'mean')
    ).reset_index()
    monthly_avg_overall_spe = data.groupby(['year_month', 'provider_specialty']).agg(
        overall_avg_amount_spe=('cost_amount', 'mean')
    ).reset_index()
    monthly_avg_overall_spe['prev_avg_amount_spe'] = monthly_avg_overall_spe.groupby('provider_specialty')['overall_avg_amount_spe'].shift(1)
    data = data.merge(monthly_avg_per_provider_spe[['year_month', 'provider_name', 'provider_specialty', 'avg_amount_spe']], 
                     on=['year_month', 'provider_name', 'provider_specialty'], how='left', suffixes=('', '_provider'))
    data = data.merge(monthly_avg_overall_spe[['year_month', 'provider_specialty', 'prev_avg_amount_spe']], 
                     on=['year_month', 'provider_specialty'], how='left')
    data['percent_diff_spe'] = ((data['avg_amount_spe'] - data['prev_avg_amount_spe']) / data['prev_avg_amount_spe']) * 100
    data['percent_diff_spe'] = data['percent_diff_spe'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
    
    # Feature 7.2: Specialty cost change for provider (direct)
    data['percent_diff_spe2'] = ((data['cost_amount'] - data['prev_avg_amount_spe']) / data['prev_avg_amount_spe']) * 100
    data['percent_diff_spe2'] = data['percent_diff_spe2'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
    
    # Feature 8.1: Service cost change for patient
    monthly_avg_per_patient = data.groupby(['year_month', 'ID', 'Service']).agg(
        avg_amount_ser_patient=('cost_amount', 'mean')
    ).reset_index()
    monthly_avg_overall_patient = data.groupby(['year_month', 'Service']).agg(
        overall_avg_amount_ser_patient=('cost_amount', 'mean')
    ).reset_index()
    monthly_avg_overall_patient['prev_avg_amount_serv_patient'] = monthly_avg_overall_patient.groupby('Service')['overall_avg_amount_ser_patient'].shift(1)
    data = data.merge(monthly_avg_per_patient[['year_month', 'ID', 'Service', 'avg_amount_ser_patient']], 
                     on=['year_month', 'ID', 'Service'], how='left', suffixes=('', '_patient'))
    data = data.merge(monthly_avg_overall_patient[['year_month', 'Service', 'prev_avg_amount_serv_patient']], 
                     on=['year_month', 'Service'], how='left')
    data['percent_diff_ser_patient'] = ((data['avg_amount_ser_patient'] - data['prev_avg_amount_serv_patient']) / data['prev_avg_amount_serv_patient']) * 100
    data.loc[data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_ser_patient'] = 0
    data['percent_diff_ser_patient'] = data['percent_diff_ser_patient'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
    
    # Feature 8.2: Service cost change (overall)
    monthly_avg_overall = data.groupby(['year_month', 'Service']).agg(
        overall_avg_amount_ser=('cost_amount', 'mean')
    ).reset_index()
    monthly_avg_overall['prev_avg_amount_ser'] = monthly_avg_overall.groupby('Service')['overall_avg_amount_ser'].shift(1)
    data = data.merge(monthly_avg_overall[['year_month', 'Service', 'prev_avg_amount_ser']], 
                     on=['year_month', 'Service'], how='left')
    data['percent_diff_serv'] = ((data['cost_amount'] - data['prev_avg_amount_ser']) / data['prev_avg_amount_ser']) * 100
    data.loc[data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_serv'] = 0
    data['percent_diff_serv'] = data['percent_diff_serv'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)
    
    # Feature 9: Service ratio
    provider_service_count = data.groupby(['provider_name', 'Service']).size().reset_index(name='Count')
    provider_count = data['provider_name'].value_counts().reset_index()
    provider_count.columns = ['provider_name', 'TotalCount']
    merged = pd.merge(provider_service_count, provider_count, on='provider_name')
    merged['Ratio'] = 1 - (merged['Count'] / merged['TotalCount'])
    merged.loc[merged['TotalCount'] == 1, 'Ratio'] = 0
    data = pd.merge(data, merged[['provider_name', 'Service', 'Ratio']], 
                   on=['provider_name', 'Service'], how='left')

def train_model():
    """Train the Isolation Forest model"""
    global data, clf, scaler, data_final
    
    # Select features
    features = ['unq_ratio_provider', 'unq_ratio_patient', 'percent_change_provider', 
                'percent_change_patient', 'percent_difference', 'percent_diff_ser', 
                'percent_diff_spe', 'percent_diff_spe2', 'percent_diff_ser_patient', 
                'percent_diff_serv', 'Ratio']
    
    # Create final dataset with features (preserve indices for alignment)
    data_final = data[features].copy()
    data_final.dropna(inplace=True)
    
    # Standardize features
    scaler = StandardScaler()
    X = scaler.fit_transform(data_final)
    
    # Train Isolation Forest
    clf = IsolationForest(
        n_estimators=200,
        max_samples=36000,
        max_features=4,
        contamination=0.2,
        random_state=42
    )
    clf.fit(X)

    # Predict on training data and enrich data_final with metadata used by charts
    y_pred = clf.predict(X)
    data_final['prediction'] = y_pred

    # Attach metadata columns aligned by original indices
    meta_columns = [
        'Adm_date', 'gender', 'age', 'Service', 'province',
        'Ins_Cover', 'Invice-type', 'Type_Medical_Record',
        'provider_name', 'ID'
    ]
    for col in meta_columns:
        if col in data.columns:
            data_final[col] = data.loc[data_final.index, col]

def predict_new_prescription(prescription_data):
    """Predict fraud for a new prescription"""
    global data, clf, scaler, data_final
    
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
    data1 = data[features1].copy()
    
    # Calculate features
    result = unique_providers_nf(data1, new_sample)
    new_sample['unq_ratio_provider'] = result['unq_ratio_provider']
    result = unique_patients_nf(data1, new_sample)
    new_sample['unq_ratio_patient'] = result['unq_ratio_patient']
    result = percent_change_provider_nf(data1, new_sample)
    new_sample['percent_change_provider'] = result['percent_change_provider']
    result = percent_change_patient_nf(data1, new_sample)
    new_sample['percent_change_patient'] = result['percent_change_patient']
    result = percent_difference_nf(data1, new_sample)
    new_sample['percent_difference'] = result['percent_difference']
    result = percent_diff_ser_nf(data1, new_sample)
    new_sample['percent_diff_ser'] = result['percent_diff_ser']
    result = percent_diff_spe_nf(data1, new_sample)
    new_sample['percent_diff_spe'] = result['percent_diff_spe']
    result = percent_diff_spe2_nf(data1, new_sample)
    new_sample['percent_diff_spe2'] = result['percent_diff_spe2']
    result = percent_diff_ser_patient_nf(data1, new_sample)
    new_sample['percent_diff_ser_patient'] = result['percent_diff_ser_patient']
    result = percent_diff_serv_nf(data1, new_sample)
    new_sample['percent_diff_serv'] = result['percent_diff_serv']
    result = ratio_nf(data1, new_sample)
    new_sample['Ratio'] = result['Ratio']
    
    # Select features for prediction
    features = ['unq_ratio_provider', 'unq_ratio_patient', 'percent_change_provider', 
                'percent_change_patient', 'percent_difference', 'percent_diff_ser', 
                'percent_diff_spe', 'percent_diff_spe2', 'percent_diff_ser_patient', 
                'percent_diff_serv', 'Ratio']
    
    new_sample_final = new_sample[features].copy()
    
    # Normalize features
    full_data = pd.concat([data_final, new_sample_final], ignore_index=True)
    scaler_temp = StandardScaler()
    scaler_temp.fit(full_data)
    normalized_array = scaler_temp.transform(new_sample_final)
    
    # Predict
    y_new_pred = clf.predict(normalized_array)
    scores_new = clf.decision_function(normalized_array)
    
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
        fraud_data = data_final[data_final['prediction'] == -1]
        fraud_counts_by_province = fraud_data['province'].value_counts()
        fraud_counts_by_province.plot(kind='bar')
        plt.xlabel('استان')
        plt.ylabel('تعداد نسخه‌های تقلبی')
        plt.title('تعداد نسخه‌های تقلبی بر اساس استان‌ها')
        plt.xticks(rotation=45)
    
    elif chart_type == 'fraud_by_gender':
        counts = data_final.groupby(['gender', 'prediction']).size().unstack(fill_value=0)
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
        data_final['age_group'] = pd.cut(data_final['age'], bins=bins, labels=labels, right=True)
        counts = data_final.groupby(['age_group', 'prediction']).size().unstack(fill_value=0)
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
        bins = [0, 4, 12, 19, 34, 49, 64, 100]
        labels = ['نوزادان', 'کودکان', 'نوجوانان', 'جوانان', 'بزرگسالان', 'میانسالان', 'سالمندان']
        data_final['age_group'] = pd.cut(data_final['age'], bins=bins, labels=labels, right=True)
        counts = data_final.groupby(['age_group', 'prediction']).size().unstack(fill_value=0)
        if 1 not in counts.columns:
            counts[1] = 0
        if -1 not in counts.columns:
            counts[-1] = 0
        ratio = (counts[-1] / (counts[1] + counts[-1])).dropna()
        ratio.sort_values().plot(kind='bar')
        plt.xlabel('گروه سنی')
        plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
        plt.title('نسبت نسخه‌های تقلبی به کل در هر گروه سنی')
        plt.xticks(rotation=45)

    elif chart_type == 'province_fraud_ratio':
        counts = data_final.groupby(['province', 'prediction']).size().unstack(fill_value=0)
        if 1 not in counts.columns:
            counts[1] = 0
        if -1 not in counts.columns:
            counts[-1] = 0
        fraud_ratio = (counts[-1] / (counts[1] + counts[-1])).sort_values(ascending=True)
        fraud_ratio.plot(kind='bar')
        plt.xlabel('استان')
        plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
        plt.title('نسبت نسخه‌های تقلبی به کل در هر استان')
        plt.xticks(rotation=45)

    elif chart_type == 'province_gender_fraud_percentage':
        total_counts = data_final.groupby(['province', 'gender']).size().unstack(fill_value=0)
        fraud_counts = data_final[data_final['prediction'] == -1].groupby(['province', 'gender']).size().unstack(fill_value=0)
        percentage_fraud = (fraud_counts / total_counts * 100).fillna(0)
        percentage_fraud.plot(kind='bar')
        plt.title('درصد نسخه‌های تقلبی در هر استان بر حسب جنسیت')
        plt.xlabel('استان‌ها')
        plt.ylabel('درصد نسخه‌های تقلبی (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()

    elif chart_type == 'fraud_counts_by_date':
        df = data_final.copy()
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
        df = data_final.copy()
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
        counts = data_final.groupby(['Ins_Cover', 'prediction']).size().unstack(fill_value=0)
        if 1 not in counts.columns:
            counts[1] = 0
        if -1 not in counts.columns:
            counts[-1] = 0
        ratio = (counts[-1] / (counts[1] + counts[-1])).dropna()
        ratio.sort_values().plot(kind='bar')
        plt.xlabel('نوع پوشش')
        plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
        plt.title('نسبت نسخه‌های تقلبی به کل در هر پوشش')
        plt.xticks(rotation=45)

    elif chart_type == 'fraud_ratio_by_invoice_type':
        col = 'Invice-type'
        counts = data_final.groupby([col, 'prediction']).size().unstack(fill_value=0)
        if 1 not in counts.columns:
            counts[1] = 0
        if -1 not in counts.columns:
            counts[-1] = 0
        ratio = (counts[-1] / (counts[1] + counts[-1])).dropna()
        ratio.sort_values().plot(kind='bar')
        plt.xlabel('نوع پوشش')
        plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
        plt.title('نسبت نسخه‌های تقلبی به کل در هر پوشش')
        plt.xticks(rotation=45)

    elif chart_type == 'fraud_ratio_by_medical_record_type':
        col = 'Type_Medical_Record'
        counts = data_final.groupby([col, 'prediction']).size().unstack(fill_value=0)
        if 1 not in counts.columns:
            counts[1] = 0
        if -1 not in counts.columns:
            counts[-1] = 0
        ratio = (counts[-1] / (counts[1] + counts[-1])).dropna()
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
        df = data_final.copy()
        if indicator not in df.columns:
            raise ValueError(f'Indicator {indicator} not found')
        # compute z-score then CDF (0-100)
        from scipy.stats import zscore, norm
        df['risk_value'] = norm.cdf(zscore(df[indicator].astype(float))) * 100
        df['Adm_date'] = pd.to_datetime(df['Adm_date'])
        df = df[df['provider_name'] == provider_name].sort_values('Adm_date')
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
        df = data_final.copy()
        if indicator not in df.columns:
            raise ValueError(f'Indicator {indicator} not found')
        from scipy.stats import zscore, norm
        df['risk_value'] = norm.cdf(zscore(df[indicator].astype(float))) * 100
        df['Adm_date'] = pd.to_datetime(df['Adm_date'])
        df = df[df['ID'] == int(patient_id)].sort_values('Adm_date')
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
        if data_final is None:
            return jsonify({'error': 'داده‌ها بارگذاری نشده‌اند'}), 500
        
        total_prescriptions = len(data_final)
        fraud_prescriptions = len(data_final[data_final['prediction'] == -1])
        normal_prescriptions = len(data_final[data_final['prediction'] == 1])
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
        'model_loaded': clf is not None,
        'data_loaded': data is not None,
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
