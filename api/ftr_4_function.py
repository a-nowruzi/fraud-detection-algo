import pandas as pd
import numpy as np

def percent_change_patient_nf(data, new_record):
    # تبدیل تاریخ به datetime اگر لازم باشد
    new_record['Adm_date'] = pd.to_datetime(new_record['Adm_date'])

    # اضافه کردن رکورد جدید به داده‌های موجود
    data = pd.concat([data, new_record], ignore_index=True)

    # محاسبه میانگین مبلغ نسخه‌ها برای هر بیمار در هر ماه  
    monthly_means = data.groupby(['year_month', 'ID']).agg(mean_amount_patient=('cost_amount', 'mean')).reset_index()  

    # محاسبه درصد تغییر از ماه گذشته  
    monthly_means['previous_mean_amount_patient_1'] = monthly_means.groupby('ID')['mean_amount_patient'].shift(1)
    monthly_means['previous_mean_amount_patient_2'] = monthly_means.groupby('ID')['mean_amount_patient'].shift(2)
    monthly_means['average_previous_mean_patient'] = monthly_means[['previous_mean_amount_patient_1', 'previous_mean_amount_patient_2']].mean(axis=1)  
    monthly_means['percent_change_patient'] = ((monthly_means['mean_amount_patient'] - monthly_means['average_previous_mean_patient']) / monthly_means['average_previous_mean_patient']) * 100  

    # ادغام نتایج با DataFrame اصلی  
    data = data.merge(monthly_means, on=['year_month', 'ID'], how='left', suffixes=('', '_monthly'))

    data['percent_change_patient'] = data['percent_change_patient'].apply(lambda x: 0 if (pd.isna(x) or x < 0 or x > 2000) else x)  
    
    # فرض بر اینکه می‌خواهید نتیجه برای رکوردم وارد شده را بگیرید
    # پیدا کردن خانه مربوطه
    last_index = data.index[-1]
    
    # برگرداندن ردیف نهایی که شامل نتایج حساب شده است
    return data.iloc[last_index]
