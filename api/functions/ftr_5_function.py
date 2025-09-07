import pandas as pd
import numpy as np

def percent_difference_nf(data, new_record):
    try:
        # تبدیل تاریخ به datetime اگر لازم باشد
        new_record['Adm_date'] = pd.to_datetime(new_record['Adm_date'])

        # اضافه کردن رکورد جدید به داده‌های موجود
        data = pd.concat([data, new_record], ignore_index=True)
 
        # محاسبه میانگین مبلغ هر خدمت در هر ماه  
        monthly_avg = data.groupby(['year_month', 'Service']).agg(avg_amount=('cost_amount', 'mean')).reset_index()

        # ادغام میانگین‌ها با DataFrame اصلی  
        data = data.merge(monthly_avg, on=['year_month', 'Service'], how='left', suffixes=('', '_monthly'))  

        # محاسبه درصد اختلاف مبلغ هر خدمت در هر نسخه نسبت به میانگین  
        data['percent_difference'] = ((data['cost_amount'] - data['avg_amount']) / data['avg_amount']) * 100  

        # صفر کردن مقادیر مربوط به خدمت "Ultrasound"  
        data.loc[data['Service'] == 'دارو و ملزومات دارویی', 'percent_difference'] = 0  

        data['percent_difference'] = data['percent_difference'].apply(lambda x: 0 if (pd.isna(x) or x < 0) else x)  

        # فرض بر اینکه می‌خواهید نتیجه برای رکوردم وارد شده را بگیرید
        # پیدا کردن خانه مربوطه
        last_index = data.index[-1]
        
        # برگرداندن ردیف نهایی که شامل نتایج حساب شده است
        return data.iloc[last_index]
    
    except Exception as e:
        print(f"Error in percent_difference_nf: {str(e)}")
        # Return a default result with the required feature
        result = pd.Series({'percent_difference': 0})
        return result
