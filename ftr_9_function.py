import pandas as pd
import numpy as np

def Ratio_nf(data, new_record):
    # تبدیل تاریخ به datetime اگر لازم باشد
    new_record['Adm_date'] = pd.to_datetime(new_record['Adm_date'])

    # اضافه کردن رکورد جدید به داده‌های موجود
    data = pd.concat([data, new_record], ignore_index=True)
 
    # محاسبه تعداد خدمات برای هر پزشک  
    provider_service_count = data.groupby(['provider_name', 'Service']).size().reset_index(name='Count')  

    # محاسبه تعداد کل نسخه های برای هر پزشک  
    provider_count = data['provider_name'].value_counts().reset_index()  
    provider_count.columns = ['provider_name', 'TotalCount']  

    # ادغام تعداد کل خدمات با تعداد خدمات برای هر پزشک  
    merged = pd.merge(provider_service_count, provider_count, on='provider_name')  

    # محاسبه نسبت خدمات نسبت به کل  
    merged['Ratio'] = 1 - (merged['Count'] / merged['TotalCount'])
    
    merged.loc[merged['TotalCount'] == 1, 'Ratio'] = 0  

    # ادغام نتایج به DataFrame اصلی براساس Specialty و Service  
    #data = pd.merge(data, merged[['provider_name', 'Service', 'Count', 'TotalCount', 'Ratio']], on=['provider_name', 'Service'], how='left')   
    data = pd.merge(
        data,
        merged[['provider_name', 'Service', 'Ratio']],  # فقط ستون‌های مورد نیاز
        on=['provider_name', 'Service'],
        how='left'
    )
    # فرض بر اینکه می‌خواهید نتیجه برای رکوردم وارد شده را بگیرید
    # پیدا کردن خانه مربوطه
    last_index = data.index[-1]
    
    # برگرداندن ردیف نهایی که شامل نتایج حساب شده است
    return data.iloc[last_index]
