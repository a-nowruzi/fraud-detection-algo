import pandas as pd
import numpy as np

import jdatetime  
from datetime import datetime    
 
# A function to add a month to a date
def add_one_month(date):  
    if date is not None:  
        next_month = date + pd.DateOffset(months=1)  
        return next_month
  
    return date 
