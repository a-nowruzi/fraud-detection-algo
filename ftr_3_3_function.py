import pandas as pd
import numpy as np

def percent_change_provider_nf(data, new_record):
    # تبدیل تاریخ به datetime اگر لازم باشد
    new_record['Adm_date'] = pd.to_datetime(new_record['Adm_date'])
    
    # اضافه کردن رکورد جدید به داده‌های موجود
    data = pd.concat([data, new_record], ignore_index=True)

    # تبدیل تاریخ به نوع datetime  
    data['Adm_date'] = pd.to_datetime(data['Adm_date'])  

    # استخراج سال و ماه  
    data['year_month'] = data['Adm_date'].dt.to_period('M')  

    # محاسبه میانگین مبلغ نسخه‌ها برای هر پزشک در هر ماه  
    monthly_means = data.groupby(['year_month', 'provider_name']).agg(mean_amount_provider=('cost_amount', 'mean')).reset_index()  

    # محاسبه درصد تغییر از ماه گذشته  

    monthly_means['previous_mean_amount_provider_1'] = monthly_means.groupby('provider_name')['mean_amount_provider'].shift(1)
    monthly_means['previous_mean_amount_provider_2'] = monthly_means.groupby('provider_name')['mean_amount_provider'].shift(2)

    monthly_means['average_previous_mean_provider'] = monthly_means[['previous_mean_amount_provider_1', 'previous_mean_amount_provider_2']].mean(axis=1)  


    monthly_means['percent_change_provider'] = ((monthly_means['mean_amount_provider'] - monthly_means['average_previous_mean_provider']) / monthly_means['average_previous_mean_provider']) * 100  

    # ادغام نتایج با DataFrame اصلی  
    data = data.merge(monthly_means, on=['year_month', 'provider_name'], how='left', suffixes=('', '_monthly'))
    data['percent_change_provider'] = data['percent_change_provider'].apply(lambda x: 0 if (pd.isna(x) or x < 0 or x > 2000) else x) 
    
    # فرض بر اینکه می‌خواهید نتیجه برای رکوردم وارد شده را بگیرید
    # پیدا کردن خانه مربوطه
    last_index = data.index[-1]
    
    # برگرداندن ردیف نهایی که شامل نتایج حساب شده است
    return data.iloc[last_index]
# نمونه استفاده:
# فرض کنید data دیتافریم اصلی است و new_record یک دیکشنری است
# نتیجه را در یک متغیر ذخیره کنید:
# result = update_and_compute(data, new_record)