import pandas as pd
import numpy as np

def percent_diff_ser_nf(data, new_record):
    # تبدیل تاریخ به datetime اگر لازم باشد
    new_record['Adm_date'] = pd.to_datetime(new_record['Adm_date'])

    # اضافه کردن رکورد جدید به داده‌های موجود
    data = pd.concat([data, new_record], ignore_index=True)
 
    
    # محاسبه میانگین مبلغ هر خدمت برای هر پزشک در هر ماه  
    monthly_avg_per_provider = data.groupby(['year_month', 'provider_name', 'Service']).agg(avg_amount_ser=('cost_amount', 'mean')).reset_index()  

    # محاسبه میانگین مبلغ هر خدمت در هر ماه  
    monthly_avg_overall = data.groupby(['year_month', 'Service']).agg(overall_avg_amount_ser=('cost_amount', 'mean')).reset_index()  

    # محاسبه میانگین ماه قبل برای هر خدمت  
    monthly_avg_overall['prev_avg_amount_serv'] = monthly_avg_overall.groupby('Service')['overall_avg_amount_ser'].shift(1)  

    # ادغام نتایج با DataFrame اصلی  
    data = data.merge(monthly_avg_per_provider[['year_month', 'provider_name', 'Service', 'avg_amount_ser']],   
                   on=['year_month', 'provider_name', 'Service'],   
                   how='left', suffixes=('', '_provider'))  

    data = data.merge(monthly_avg_overall[['year_month', 'Service', 'prev_avg_amount_serv']],   
                   on=['year_month', 'Service'],   
                   how='left')

    # محاسبه درصد اختلاف  
    data['percent_diff_ser'] = ((data['avg_amount_ser'] - data['prev_avg_amount_serv']) / data['prev_avg_amount_serv']) * 100  

    # صفر کردن مقادیر مربوط به خدمت "Ultrasound"  
  
    data.loc[data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_ser'] = 0

    data['percent_diff_ser'] = data['percent_diff_ser'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)

    # نمایش نتایج نهایی  
    #result = data[['Adm_date', 'cost_amount', 'prev_avg_amount_serv','percent_diff_ser']]  
    #print(result)

    # فرض بر اینکه می‌خواهید نتیجه برای رکوردم وارد شده را بگیرید
    # پیدا کردن خانه مربوطه
    last_index = data.index[-1]
    
    # برگرداندن ردیف نهایی که شامل نتایج حساب شده است
    return data.iloc[last_index]
