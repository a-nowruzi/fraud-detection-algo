import pandas as pd
import numpy as np

def percent_diff_ser_patient_nf(data, new_record):
    # تبدیل تاریخ به datetime اگر لازم باشد
    new_record['Adm_date'] = pd.to_datetime(new_record['Adm_date'])

    # اضافه کردن رکورد جدید به داده‌های موجود
    data = pd.concat([data, new_record], ignore_index=True)
 

    # محاسبه میانگین مبلغ هر خدمت برای هر بیمار در هر ماه  
    monthly_avg_per_patient = data.groupby(['year_month', 'ID', 'Service']).agg(avg_amount_ser_patient=('cost_amount', 'mean')).reset_index()  

    # محاسبه میانگین مبلغ هر خدمت در هر ماه  
    monthly_avg_overall_patient = data.groupby(['year_month', 'Service']).agg(overall_avg_amount_ser_patient=('cost_amount', 'mean')).reset_index()  

    # محاسبه میانگین ماه قبل برای هر خدمت  
    monthly_avg_overall_patient['prev_avg_amount_serv_patient'] = monthly_avg_overall_patient.groupby('Service')['overall_avg_amount_ser_patient'].shift(1)  

    # ادغام نتایج با DataFrame اصلی  
    data = data.merge(monthly_avg_per_patient[['year_month', 'ID', 'Service', 'avg_amount_ser_patient']],   
                   on=['year_month', 'ID', 'Service'],   
                   how='left', suffixes=('', '_patient'))  

    data = data.merge(monthly_avg_overall_patient[['year_month', 'Service', 'prev_avg_amount_serv_patient']],   
                   on=['year_month', 'Service'],   
                   how='left')

    # محاسبه درصد اختلاف  
    data['percent_diff_ser_patient'] = ((data['avg_amount_ser_patient'] - data['prev_avg_amount_serv_patient']) / data['prev_avg_amount_serv_patient']) * 100  
    data.loc[data['Service'] == 'دارو و ملزومات دارویی', 'percent_diff_ser_patient'] = 0 
    data['percent_diff_ser_patient'] = data['percent_diff_ser_patient'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x) 
    # فرض بر اینکه می‌خواهید نتیجه برای رکوردم وارد شده را بگیرید
    # پیدا کردن خانه مربوطه
    last_index = data.index[-1]
    
    # برگرداندن ردیف نهایی که شامل نتایج حساب شده است
    return data.iloc[last_index]
