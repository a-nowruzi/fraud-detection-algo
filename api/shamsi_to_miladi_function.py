import pandas as pd
import numpy as np

import jdatetime  
from datetime import datetime  

# تابعی برای تبدیل تاریخ شمسی به میلادی  
def shamsi_to_miladi(date_str):  
    if pd.isnull(date_str):  
        return None  
    return jdatetime.datetime.strptime(date_str, "%Y/%m/%d").togregorian()  
