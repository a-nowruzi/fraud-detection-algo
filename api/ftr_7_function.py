import pandas as pd
import numpy as np

def percent_diff_spe_nf(data, new_record):
    # تبدیل تاریخ به datetime اگر لازم باشد
    new_record['Adm_date'] = pd.to_datetime(new_record['Adm_date'])

    # اضافه کردن رکورد جدید به داده‌های موجود
    data = pd.concat([data, new_record], ignore_index=True)
 
    
    # محاسبه میانگین مبلغ هر تخصص برای هر پزشک در هر ماه  
    monthly_avg_per_provider_spe = data.groupby(['year_month', 'provider_name', 'provider_specialty']).agg(avg_amount_spe=('cost_amount', 'mean')).reset_index()  

    # محاسبه میانگین مبلغ هر خدمت در هر ماه  
    monthly_avg_overall_spe = data.groupby(['year_month', 'provider_specialty']).agg(overall_avg_amount_spe=('cost_amount', 'mean')).reset_index()  

    # محاسبه میانگین ماه قبل برای هر خدمت  
    monthly_avg_overall_spe['prev_avg_amount_spe'] = monthly_avg_overall_spe.groupby('provider_specialty')['overall_avg_amount_spe'].shift(1)  

    # ادغام نتایج با DataFrame اصلی  
    data = data.merge(monthly_avg_per_provider_spe[['year_month', 'provider_name', 'provider_specialty', 'avg_amount_spe']],   
                   on=['year_month', 'provider_name', 'provider_specialty'],   
                   how='left', suffixes=('', '_provider'))  

    data = data.merge(monthly_avg_overall_spe[['year_month', 'provider_specialty', 'prev_avg_amount_spe']],   
                   on=['year_month', 'provider_specialty'],   
                   how='left')

    # محاسبه درصد اختلاف  
    data['percent_diff_spe'] = ((data['avg_amount_spe'] - data['prev_avg_amount_spe']) / data['prev_avg_amount_spe']) * 100  
    data['percent_diff_spe'] = data['percent_diff_spe'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x) 

    # فرض بر اینکه می‌خواهید نتیجه برای رکوردم وارد شده را بگیرید
    # پیدا کردن خانه مربوطه
    last_index = data.index[-1]
    
    # برگرداندن ردیف نهایی که شامل نتایج حساب شده است
    return data.iloc[last_index]
