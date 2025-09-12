import pandas as pd
import numpy as np


def unique_patients_nf(data, new_record):
    # اضافه کردن رکورد جدید به داده‌های موجود
    data = pd.concat([data, new_record], ignore_index=True)
    ## total number of providers per month for each patient per prescription
  
    # محاسبه تعداد کل بیماران (شامل تکراری) ماهانه برای هر پزشک  
    patients_count_per_month = data.groupby(['year_month', 'provider_name']).agg(  
        total_patients_monthly=('ID', 'count')  # تعداد کل بیماران  
    ).reset_index()  

    # ادغام اطلاعات بیماران با DataFrame اصلی  
    data = data.merge(patients_count_per_month, on=['year_month', 'provider_name'], how='left')  

    # محاسبه تعداد پزشکان منحصر به فرد ماهانه برای هر یبمار  
    unique_patients_per_month = data.groupby(['year_month', 'provider_name']).agg(  
        unique_patients=('ID', 'nunique')  # تعداد پزشکان منحصر به فرد  
    ).reset_index()  

    # ادغام اطلاعات منحصر به فرد بیماران با DataFrame اصلی  
    data = data.merge(unique_patients_per_month, on=['year_month', 'provider_name'], how='left')  
    data['unq_ratio_patient']= data['total_patients_monthly'] / data ['unique_patients']  

    # فرض بر اینکه می‌خواهید نتیجه برای رکوردم وارد شده را بگیرید
    # پیدا کردن خانه مربوطه
    last_index = data.index[-1]
    
    # برگرداندن ردیف نهایی که شامل نتایج حساب شده است
    return data.iloc[last_index]