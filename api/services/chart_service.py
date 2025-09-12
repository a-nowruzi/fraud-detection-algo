"""
Chart generation service for fraud detection API
سرویس تولید نمودار برای API تشخیص تقلب
"""

import matplotlib
# Set backend to Agg before importing pyplot to avoid tkinter issues in server environment
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
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
import arabic_reshaper
from bidi.algorithm import get_display
import os

logger = logging.getLogger(__name__)

class ChartService:
    """Service for generating various charts and visualizations"""
    
    def __init__(self, data_final: pd.DataFrame):
        self.data_final = data_final
        plt.style.use('default')  # Reset to default style
        self._configure_persian_fonts()
    
    def _configure_persian_fonts(self):
        """Configure matplotlib for Persian text rendering"""
        try:
            # Use Vazir font from assets directory
            font_paths = [
                'assets/Vazir-Medium-FD.ttf',  # Primary Vazir font
                'api/assets/Vazir-Medium-FD.ttf',  # Alternative path
                'assets/Estedad-Medium.ttf',  # Fallback Estedad font
                'api/assets/Estedad-Medium.ttf',  # Alternative Estedad path
            ]
            
            font_path = None
            for path in font_paths:
                if os.path.exists(path):
                    font_path = path
                    break
            
            if font_path:
                # Register the font
                fm.fontManager.addfont(font_path)
                font_name = fm.FontProperties(fname=font_path).get_name()
                plt.rcParams['font.family'] = font_name
                logger.info(f"Persian font configured: {font_name} from {font_path}")
            else:
                # Fallback to default font with Unicode support
                plt.rcParams['font.family'] = 'DejaVu Sans'
                logger.warning("Vazir font not found in assets directory, using fallback font")
                
            # Configure matplotlib for better text rendering
            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['figure.autolayout'] = True
            
        except Exception as e:
            logger.error(f"Error configuring Persian fonts: {str(e)}")
            # Fallback configuration
            plt.rcParams['font.family'] = 'DejaVu Sans'
            plt.rcParams['axes.unicode_minus'] = False
    
    def _prepare_persian_text(self, text: str) -> str:
        """Prepare Persian text for matplotlib rendering"""
        try:
            if not text or not isinstance(text, str):
                return text
            
            # Reshape Arabic/Persian text
            reshaped_text = arabic_reshaper.reshape(text)
            # Apply bidirectional algorithm
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            logger.warning(f"Error processing Persian text '{text}': {str(e)}")
            return text
    
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
        fig = None
        try:
            # Create figure with error handling
            fig = plt.figure(figsize=app_config.chart_figsize)
            
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
            # Ensure all plots are closed properly
            if fig is not None:
                plt.close(fig)
            plt.close('all')  # Close any remaining figures
    
    def _create_risk_indicators_chart(self, risk_values: List[float]) -> str:
        """Create risk indicators bar chart"""
        try:
            risk_indices = [
                'نسبت منحصر به فرد ارائه‌دهنده', 'نسبت منحصر به فرد بیمار', 'درصد تغییر ارائه‌دهنده',
                'درصد تغییر بیمار', 'درصد تفاوت', 'درصد تفاوت خدمت',
                'درصد تفاوت تخصص', 'درصد تفاوت تخصص 2', 'درصد تفاوت خدمت بیمار',
                'درصد تفاوت خدمات', 'نسبت'
            ]
            
            # Validate risk_values
            if not risk_values or len(risk_values) == 0:
                logger.warning("No risk values provided for risk indicators chart")
                risk_values = [0] * len(risk_indices)
            elif len(risk_values) != len(risk_indices):
                logger.warning(f"Risk values length ({len(risk_values)}) doesn't match indices length ({len(risk_indices)})")
                # Pad or truncate to match
                if len(risk_values) < len(risk_indices):
                    risk_values.extend([0] * (len(risk_indices) - len(risk_values)))
                else:
                    risk_values = risk_values[:len(risk_indices)]
            
            # Ensure all values are numeric and within reasonable range
            risk_values = [float(val) if val is not None else 0.0 for val in risk_values]
            risk_values = [max(0, min(100, val)) for val in risk_values]  # Clamp between 0 and 100
            
            # Prepare Persian text for labels
            risk_indices_persian = [self._prepare_persian_text(idx) for idx in risk_indices]
            
            plt.bar(risk_indices_persian, risk_values, color='skyblue')
            plt.xlabel(self._prepare_persian_text('شاخص‌های ریسک'))
            plt.ylabel(self._prepare_persian_text('مقدار شاخص ریسک (0 تا 100)'))
            plt.title(self._prepare_persian_text('مقدار هر یک از شاخص‌های ریسک نسخه پزشکی'))
            plt.xticks(rotation=90, ha='center')
            plt.tight_layout()
            
            return self._figure_to_base64()
            
        except Exception as e:
            logger.error(f"Error creating risk indicators chart: {str(e)}")
            raise ChartGenerationError(f"Failed to create risk indicators chart: {str(e)}", chart_type="risk_indicators")
    
    def _create_fraud_by_province_chart(self) -> str:
        """Create fraud by province bar chart"""
        fraud_data = self.data_final[self.data_final['prediction'] == -1]
        fraud_counts_by_province = fraud_data['province'].value_counts()
        
        # Prepare Persian text for province names
        province_names_persian = [self._prepare_persian_text(name) for name in fraud_counts_by_province.index]
        
        plt.bar(province_names_persian, fraud_counts_by_province.values)
        plt.xlabel(self._prepare_persian_text('استان'))
        plt.ylabel(self._prepare_persian_text('تعداد نسخه‌های تقلبی'))
        plt.title(self._prepare_persian_text('تعداد نسخه‌های تقلبی بر اساس استان‌ها'))
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
        # Prepare Persian text for gender labels
        gender_labels_persian = [self._prepare_persian_text(label) for label in ratios.index]
        
        plt.pie(ratios, labels=gender_labels_persian, autopct='%.2f%%', startangle=90)
        plt.title(self._prepare_persian_text('نسبت نسخه‌های تقلبی به کل نسخه ها بر اساس جنسیت'))
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
        # Prepare Persian text for age group labels
        age_labels_persian = [self._prepare_persian_text(label) for label in ratios.index]
        
        plt.pie(ratios, labels=age_labels_persian, autopct='%.2f%%', startangle=90)
        plt.title(self._prepare_persian_text('نسبت نسخه‌های تقلبی به نرمال بر اساس گروه سنی'))
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
        # Prepare Persian text for age group labels
        age_group_labels_persian = [self._prepare_persian_text(label) for label in ratio.index]
        
        plt.bar(age_group_labels_persian, ratio.values)
        plt.xlabel(self._prepare_persian_text('گروه سنی'))
        plt.ylabel(self._prepare_persian_text('نسبت نسخه‌های تقلبی به کل نسخه‌ها'))
        plt.title(self._prepare_persian_text('نسبت نسخه‌های تقلبی به کل در هر گروه سنی'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_province_fraud_ratio_chart(self) -> str:
        """Create province fraud ratio bar chart"""
        counts = self.data_final.groupby(['province', 'prediction']).size().unstack(fill_value=0)
        fraud_ratio = self._calculate_fraud_ratio(counts)
        sorted_ratio = fraud_ratio.sort_values(ascending=True)
        # Prepare Persian text for province names
        province_names_persian = [self._prepare_persian_text(name) for name in sorted_ratio.index]
        
        plt.bar(province_names_persian, sorted_ratio.values)
        plt.xlabel(self._prepare_persian_text('استان'))
        plt.ylabel(self._prepare_persian_text('نسبت نسخه‌های تقلبی به کل نسخه‌ها'))
        plt.title(self._prepare_persian_text('نسبت نسخه‌های تقلبی به کل در هر استان'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_province_gender_fraud_percentage_chart(self) -> str:
        """Create province gender fraud percentage chart"""
        total_counts = self.data_final.groupby(['province', 'gender']).size().unstack(fill_value=0)
        fraud_counts = self.data_final[self.data_final['prediction'] == -1].groupby(['province', 'gender']).size().unstack(fill_value=0)
        percentage_fraud = (fraud_counts / total_counts * 100).fillna(0)
        # Prepare Persian text for province names
        province_names_persian = [self._prepare_persian_text(name) for name in percentage_fraud.index]
        
        plt.bar(province_names_persian, percentage_fraud.values)
        plt.title(self._prepare_persian_text('درصد نسخه‌های تقلبی در هر استان بر حسب جنسیت'))
        plt.xlabel(self._prepare_persian_text('استان‌ها'))
        plt.ylabel(self._prepare_persian_text('درصد نسخه‌های تقلبی (%)'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_fraud_counts_by_date_chart(self) -> str:
        """Create fraud counts by date line chart"""
        df = self.data_final.copy()
        df['Adm_date'] = pd.to_datetime(df['Adm_date'])
        fraud_by_date = df[df['prediction'] == -1].groupby('Adm_date').size()
        ax = fraud_by_date.plot()
        ax.set_xlabel(self._prepare_persian_text('تاریخ پذیرش نسخه'))
        ax.set_ylabel(self._prepare_persian_text('تعداد نسخه تقلبی'))
        ax.set_title(self._prepare_persian_text('تعداد نسخه‌های تقلبی بر حسب تاریخ پذیرش'))
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
        ax.set_xlabel(self._prepare_persian_text('تاریخ پذیرش نسخه'))
        ax.set_ylabel(self._prepare_persian_text('نسبت نسخه تقلبی به کل نسخه‌ها'))
        ax.set_title(self._prepare_persian_text('نسبت نسخه‌های تقلبی بر حسب تاریخ پذیرش'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.grid(True)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_fraud_ratio_by_ins_cover_chart(self) -> str:
        """Create fraud ratio by insurance cover chart"""
        counts = self.data_final.groupby(['Ins_Cover', 'prediction']).size().unstack(fill_value=0)
        ratio = self._calculate_fraud_ratio(counts)
        sorted_ratio = ratio.sort_values()
        # Prepare Persian text for insurance cover labels
        cover_labels_persian = [self._prepare_persian_text(label) for label in sorted_ratio.index]
        
        plt.bar(cover_labels_persian, sorted_ratio.values)
        plt.xlabel(self._prepare_persian_text('نوع پوشش'))
        plt.ylabel(self._prepare_persian_text('نسبت نسخه‌های تقلبی به کل نسخه‌ها'))
        plt.title(self._prepare_persian_text('نسبت نسخه‌های تقلبی به کل در هر پوشش'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_fraud_ratio_by_invoice_type_chart(self) -> str:
        """Create fraud ratio by invoice type chart"""
        col = 'Invice-type'
        counts = self.data_final.groupby([col, 'prediction']).size().unstack(fill_value=0)
        ratio = self._calculate_fraud_ratio(counts)
        sorted_ratio = ratio.sort_values()
        # Prepare Persian text for invoice type labels
        invoice_labels_persian = [self._prepare_persian_text(label) for label in sorted_ratio.index]
        
        plt.bar(invoice_labels_persian, sorted_ratio.values)
        plt.xlabel(self._prepare_persian_text('نوع فاکتور'))
        plt.ylabel(self._prepare_persian_text('نسبت نسخه‌های تقلبی به کل نسخه‌ها'))
        plt.title(self._prepare_persian_text('نسبت نسخه‌های تقلبی به کل در هر نوع فاکتور'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._figure_to_base64()
    
    def _create_fraud_ratio_by_medical_record_type_chart(self) -> str:
        """Create fraud ratio by medical record type chart"""
        col = 'Type_Medical_Record'
        counts = self.data_final.groupby([col, 'prediction']).size().unstack(fill_value=0)
        ratio = self._calculate_fraud_ratio(counts)
        sorted_ratio = ratio.sort_values()
        # Prepare Persian text for medical record type labels
        record_labels_persian = [self._prepare_persian_text(label) for label in sorted_ratio.index]
        
        plt.bar(record_labels_persian, sorted_ratio.values)
        plt.xlabel(self._prepare_persian_text('نوع پرونده پزشکی'))
        plt.ylabel(self._prepare_persian_text('نسبت نسخه‌های تقلبی به کل نسخه‌ها'))
        plt.title(self._prepare_persian_text('نسبت نسخه‌های تقلبی به کل در هر نوع پرونده'))
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
        plt.title(self._prepare_persian_text(f'شاخص ریسک {indicator} برای پزشک {provider_name}'))
        plt.xlabel(self._prepare_persian_text('تاریخ نسخه'))
        plt.ylabel(self._prepare_persian_text('شاخص ریسک (0-100)'))
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
        plt.title(self._prepare_persian_text(f'شاخص ریسک {indicator} برای بیمار {patient_id}'))
        plt.xlabel(self._prepare_persian_text('تاریخ نسخه'))
        plt.ylabel(self._prepare_persian_text('شاخص ریسک (0-100)'))
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
