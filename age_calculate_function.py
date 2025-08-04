import pandas as pd
import numpy as np

import jdatetime  
from datetime import datetime    

# تابع برای محاسبه سن  
def calculate_age(sh_date):  
    # تقسیم رشته تاریخ به اجزا  
    year, month, day = map(int, sh_date.split('/'))  
    
    # تبدیل تاریخ شمسی به تاریخ میلادی  
    jalali_date = jdatetime.date(year, month, day).togregorian()  

    # تاریخ فعلی  
    today = datetime.now()  

    # محاسبه سن  
    age = today.year - jalali_date.year  

    # بررسی اینکه آیا تولد امسال رخ داده یا نه  
    if (today.month, today.day) < (jalali_date.month, jalali_date.day):  
        age -= 1  

    return age  
