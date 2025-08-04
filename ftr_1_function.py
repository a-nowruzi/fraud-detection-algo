import pandas as pd
import numpy as np


def unique_providers_nf(data, new_record):
    # اضافه کردن رکورد جدید به داده‌های موجود
    data = pd.concat([data, new_record], ignore_index=True)
  
    # محاسبه تعداد کل بیماران (شامل تکراری) ماهانه برای هر پزشک  
    providers_count_per_month = data.groupby(['year_month', 'ID']).agg(  
        total_providers_monthly=('provider_name', 'count')  # تعداد کل بیماران  
    ).reset_index()  

    # ادغام اطلاعات بیماران با DataFrame اصلی  
    data = data.merge(providers_count_per_month, on=['year_month', 'ID'], how='left')  

    # محاسبه تعداد پزشکان منحصر به فرد ماهانه برای هر یبمار  
    unique_providers_per_month = data.groupby(['year_month', 'ID']).agg(  
        unique_providers=('provider_name', 'nunique')  # تعداد پزشکان منحصر به فرد  
    ).reset_index()  

    # ادغام اطلاعات منحصر به فرد بیماران با DataFrame اصلی  
    data = data.merge(unique_providers_per_month, on=['year_month', 'ID'], how='left') 
    data['unq_ratio_provider']= data['total_providers_monthly'] / data ['unique_providers']  
    
    
    # فرض بر اینکه می‌خواهید نتیجه برای رکوردم وارد شده را بگیرید
    # پیدا کردن خانه مربوطه
    last_index = data.index[-1]
    
    # برگرداندن ردیف نهایی که شامل نتایج حساب شده است
    return data.iloc[last_index]