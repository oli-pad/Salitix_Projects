import pandas as pd
import os
from sys import argv

script,img_path,exceptions_path,exceptions_file=argv

df=pd.read_csv(os.path.join(exceptions_path,exceptions_file))

for i in df.index:
    filename="100"+str(df[" Retailer_Invoice"].loc[i])
    if os.path.exists(os.path.join(img_path,filename+".pdf")):
        df[" Corrected_Invoice_Number"].loc[i]=filename
        df[" Invoice_Status"].loc[i]="Found"
    else:
        df[" Invoice_Status"].loc[i]="Not Found"

df.to_csv(r"C:\Users\Python\Desktop\Tesco test\Test.csv",index=False)
