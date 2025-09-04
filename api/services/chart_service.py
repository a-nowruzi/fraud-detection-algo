"""
Chart generation service for fraud detection API
سرویس تولید نمودار برای API تشخیص تقلب
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import seaborn as sns
import io
import base64
from typing import Dict, Any, List, Optional
from scipy.stats import zscore, norm
from config.config import app_config
from core.exceptions import ChartGenerationError
import logging

logger = logging.getLogger(__name__)

class ChartService:
    """Service for generating various charts and visualizations"""
    
    def __init__(self, data_final: pd.DataFrame):
        self.data_final = data_final
        plt.style.use('default')  # Reset to default style
    
    def create_chart(self, chart_type: str, **kwargs) -> str:
        """
        Create various charts and return as base64 string
        
        Args:
            chart_type: Type of chart to create
            **kwargs: Additional parameters for specific chart types
            
        Returns:
            Base64 encoded PNG image string
            
        Raises:
            ChartGenerationError: If chart generation fails
        """
        try:
            plt.figure(figsize=app_config.chart_figsize)
            
            if chart_type == 'risk_indicators':
                return self._create_risk_indicators_chart(**kwargs)
            elif chart_type == 'fraud_by_province':
                return self._create_fraud_by_province_chart()
            elif chart_type == 'fraud_by_gender':
                return self._create_fraud_by_gender_chart()
            elif chart_type == 'fraud_by_age_group':
                return self._create_fraud_by_age_group_chart()
            elif chart_type == 'fraud_ratio_by_age_group':
                return self._create_fraud_ratio_by_age_group_chart()
            elif chart_type == 'province_fraud_ratio':
                return self._create_province_fraud_ratio_chart()
            elif chart_type == 'province_gender_fraud_percentage':
                return self._create_province_gender_fraud_percentage_chart()
            elif chart_type == 'fraud_counts_by_date':
                return self._create_fraud_counts_by_date_chart()
            elif chart_type == 'fraud_ratio_by_date':
                return self._create_fraud_ratio_by_date_chart()
            elif chart_type == 'fraud_ratio_by_ins_cover':
                return self._create_fraud_ratio_by_ins_cover_chart()
            elif chart_type == 'fraud_ratio_by_invoice_type':
                return self._create_fraud_ratio_by_invoice_type_chart()
            elif chart_type == 'fraud_ratio_by_medical_record_type':
                return self._create_fraud_ratio_by_medical_record_type_chart()
            elif chart_type == 'provider_risk_indicator_time_series':
                return self._create_provider_risk_indicator_time_series_chart(**kwargs)
            elif chart_type == 'patient_risk_indicator_time_series':
                return self._create_patient_risk_indicator_time_series_chart(**kwargs)
            else:
                raise ChartGenerationError(f"Unknown chart type: {chart_type}", chart_type=chart_type)
                
        except Exception as e:
            logger.error(f"Error creating chart {chart_type}: {str(e)}")
            raise ChartGenerationError(f"Failed to create chart: {str(e)}", chart_type=chart_type)
        finally:
            plt.close('all')  # Ensure all plots are closed
    
    def _create_risk_indicators_chart(self, risk_values: List[float]) -> str:
        """Create risk indicators bar chart"""
        risk_indices = [
            'unq_ratio_provider', 'unq_ratio_patient', 'percent_change_provider',
            'percent_change_patient', 'percent_difference', 'percent_diff_ser',
            'percent_diff_spe', 'percent_diff_spe2', 'percent_diff_ser_patient',
            'percent_diff_serv', 'Ratio'
        ]
        
        plt.bar(risk_indices, risk_values, color='skyblue')
        plt.xlabel('شاخص‌های ریسک')
        plt.ylabel('مقدار شاخص ریسک (0 تا 100)')
        plt.title('مقدار هر یک از شاخص‌های ریسک نسخه پزشکی')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_fraud_by_province_chart(self) -> str:
        """Create fraud by province bar chart"""
        fraud_data = self.data_final[self.data_final['prediction'] == -1]
        fraud_counts_by_province = fraud_data['province'].value_counts()
        fraud_counts_by_province.plot(kind='bar')
        plt.xlabel('استان')
        plt.ylabel('تعداد نسخه‌های تقلبی')
        plt.title('تعداد نسخه‌های تقلبی بر اساس استان‌ها')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_fraud_by_gender_chart(self) -> str:
        """Create fraud by gender pie chart"""
        counts = self.data_final.groupby(['gender', 'prediction']).size().unstack(fill_value=0)
        if 1 not in counts.columns:
            counts[1] = 0
        if -1 not in counts.columns:
            counts[-1] = 0
        ratios = counts.apply(
            lambda row: row[-1] / (row[1] + row[-1]) if (row[1] + row[-1]) != 0 else 0, axis=1
        )
        plt.pie(ratios, labels=ratios.index, autopct='%.2f%%', startangle=90)
        plt.title('نسبت نسخه‌های تقلبی به کل نسخه ها بر اساس جنسیت')
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_fraud_by_age_group_chart(self) -> str:
        """Create fraud by age group pie chart"""
        self.data_final['age_group'] = pd.cut(
            self.data_final['age'], 
            bins=app_config.age_bins, 
            labels=app_config.age_labels, 
            right=True
        )
        counts = self.data_final.groupby(['age_group', 'prediction']).size().unstack(fill_value=0)
        if 1 not in counts.columns:
            counts[1] = 0
        if -1 not in counts.columns:
            counts[-1] = 0
        ratios = counts.apply(
            lambda row: row[-1] / (row[1] + row[-1]) if (row[1] + row[-1]) != 0 else 0, axis=1
        )
        plt.pie(ratios, labels=ratios.index, autopct='%.2f%%', startangle=90)
        plt.title('نسبت نسخه‌های تقلبی به نرمال بر اساس گروه سنی')
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_fraud_ratio_by_age_group_chart(self) -> str:
        """Create fraud ratio by age group bar chart"""
        self.data_final['age_group'] = pd.cut(
            self.data_final['age'], 
            bins=app_config.age_bins, 
            labels=app_config.age_labels, 
            right=True
        )
        counts = self.data_final.groupby(['age_group', 'prediction']).size().unstack(fill_value=0)
        ratio = self._calculate_fraud_ratio(counts)
        ratio.sort_values().plot(kind='bar')
        plt.xlabel('گروه سنی')
        plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
        plt.title('نسبت نسخه‌های تقلبی به کل در هر گروه سنی')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_province_fraud_ratio_chart(self) -> str:
        """Create province fraud ratio bar chart"""
        counts = self.data_final.groupby(['province', 'prediction']).size().unstack(fill_value=0)
        fraud_ratio = self._calculate_fraud_ratio(counts)
        fraud_ratio.sort_values(ascending=True).plot(kind='bar')
        plt.xlabel('استان')
        plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
        plt.title('نسبت نسخه‌های تقلبی به کل در هر استان')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_province_gender_fraud_percentage_chart(self) -> str:
        """Create province gender fraud percentage chart"""
        total_counts = self.data_final.groupby(['province', 'gender']).size().unstack(fill_value=0)
        fraud_counts = self.data_final[self.data_final['prediction'] == -1].groupby(['province', 'gender']).size().unstack(fill_value=0)
        percentage_fraud = (fraud_counts / total_counts * 100).fillna(0)
        percentage_fraud.plot(kind='bar')
        plt.title('درصد نسخه‌های تقلبی در هر استان بر حسب جنسیت')
        plt.xlabel('استان‌ها')
        plt.ylabel('درصد نسخه‌های تقلبی (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_fraud_counts_by_date_chart(self) -> str:
        """Create fraud counts by date line chart"""
        df = self.data_final.copy()
        df['Adm_date'] = pd.to_datetime(df['Adm_date'])
        fraud_by_date = df[df['prediction'] == -1].groupby('Adm_date').size()
        ax = fraud_by_date.plot()
        ax.set_xlabel('تاریخ پذیرش نسخه')
        ax.set_ylabel('تعداد نسخه تقلبی')
        ax.set_title('تعداد نسخه‌های تقلبی بر حسب تاریخ پذیرش')
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.grid(True)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_fraud_ratio_by_date_chart(self) -> str:
        """Create fraud ratio by date line chart"""
        df = self.data_final.copy()
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
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_fraud_ratio_by_ins_cover_chart(self) -> str:
        """Create fraud ratio by insurance cover chart"""
        counts = self.data_final.groupby(['Ins_Cover', 'prediction']).size().unstack(fill_value=0)
        ratio = self._calculate_fraud_ratio(counts)
        ratio.sort_values().plot(kind='bar')
        plt.xlabel('نوع پوشش')
        plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
        plt.title('نسبت نسخه‌های تقلبی به کل در هر پوشش')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_fraud_ratio_by_invoice_type_chart(self) -> str:
        """Create fraud ratio by invoice type chart"""
        col = 'Invice-type'
        counts = self.data_final.groupby([col, 'prediction']).size().unstack(fill_value=0)
        ratio = self._calculate_fraud_ratio(counts)
        ratio.sort_values().plot(kind='bar')
        plt.xlabel('نوع پوشش')
        plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
        plt.title('نسبت نسخه‌های تقلبی به کل در هر پوشش')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_fraud_ratio_by_medical_record_type_chart(self) -> str:
        """Create fraud ratio by medical record type chart"""
        col = 'Type_Medical_Record'
        counts = self.data_final.groupby([col, 'prediction']).size().unstack(fill_value=0)
        ratio = self._calculate_fraud_ratio(counts)
        ratio.sort_values().plot(kind='bar')
        plt.xlabel('نوع پرونده پزشکی')
        plt.ylabel('نسبت نسخه‌های تقلبی به کل نسخه‌ها')
        plt.title('نسبت نسخه‌های تقلبی به کل در هر نوع پرونده')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_provider_risk_indicator_time_series_chart(self, provider_name: str, indicator: str) -> str:
        """Create provider risk indicator time series chart"""
        if indicator not in self.data_final.columns:
            raise ChartGenerationError(f"Indicator {indicator} not found", chart_type="provider_risk_indicator_time_series")
        
        df = self.data_final.copy()
        df['risk_value'] = norm.cdf(zscore(df[indicator].astype(float))) * 100
        df['Adm_date'] = pd.to_datetime(df['Adm_date'])
        df = df[df['provider_name'] == provider_name].sort_values('Adm_date')
        
        sns.lineplot(data=df, x='Adm_date', y='risk_value', marker='o')
        plt.title(f'شاخص ریسک {indicator} برای پزشک {provider_name}')
        plt.xlabel('تاریخ نسخه')
        plt.ylabel('شاخص ریسک (0-100)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_patient_risk_indicator_time_series_chart(self, patient_id: int, indicator: str) -> str:
        """Create patient risk indicator time series chart"""
        if indicator not in self.data_final.columns:
            raise ChartGenerationError(f"Indicator {indicator} not found", chart_type="patient_risk_indicator_time_series")
        
        df = self.data_final.copy()
        df['risk_value'] = norm.cdf(zscore(df[indicator].astype(float))) * 100
        df['Adm_date'] = pd.to_datetime(df['Adm_date'])
        df = df[df['ID'] == int(patient_id)].sort_values('Adm_date')
        
        sns.lineplot(data=df, x='Adm_date', y='risk_value', marker='o')
        plt.title(f'شاخص ریسک {indicator} برای بیمار {patient_id}')
        plt.xlabel('تاریخ نسخه')
        plt.ylabel('شاخص ریسک (0-100)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _calculate_fraud_ratio(self, counts: pd.DataFrame) -> pd.Series:
        """Calculate fraud ratio from prediction counts"""
        if 1 not in counts.columns:
            counts[1] = 0
        if -1 not in counts.columns:
            counts[-1] = 0
        return (counts[-1] / (counts[1] + counts[-1])).dropna()
    
    def _figure_to_base64(self) -> str:
        """Convert matplotlib figure to base64 string"""
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=app_config.chart_dpi)
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode()
