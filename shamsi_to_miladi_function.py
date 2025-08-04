import pandas as pd
import numpy as np

import jdatetime  
from datetime import datetime  

# تابعی برای تبدیل تاریخ شمسی به میلادی  
def convert_to_gregorian(date_str):  
    if pd.isnull(date_str):  
        return None  
    return jdatetime.datetime.strptime(date_str, "%Y/%m/%d").togregorian()  
