import pandas as pd
from sklearn.preprocessing import StandardScaler

def normalize_features(df1, df2):
    # مرحله 1: ادغام مجموعه داده‌ها
    full_data = pd.concat([df1, df2], ignore_index=True)
    
    # مرحله 2: آموزش نرمال‌سازی بر روی مجموعه اول (بدون رکورد دوم)
    scaler = StandardScaler()
    scaler.fit(full_data)
    
    # رکورد آخر (مربوط به مجموعه دوم)
    last_record = full_data.iloc[[-1]]
    
    # نرمال‌سازی رکورد آخر
    normalized_last = scaler.transform(last_record)
    normalized_array = normalized_last  # آرایه نرمال‌شده
    
    # (اختیاری) جایگزینی رکورد نرمال‌شده در داده‌ها
    full_data.iloc[-1] = normalized_array
    
    # خروجی: آرایه نرمال‌شده آخرین رکورد
    return normalized_array