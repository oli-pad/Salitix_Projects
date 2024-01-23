import pandas as pd
import os
import shutil
from sys import argv

script,img_path,exceptions_path,exceptions_file=argv

df=pd.read_csv(os.path.join(exceptions_path,exceptions_file))

for i in df.index:
    filename=str(df["Invoice_Name"].loc[i])
    if os.path.exists(os.path.join(img_path,filename+".pdf")):
        shutil.copyfile(os.path.join(img_path,filename+".pdf"),os.path.join(r"C:\Users\Python\Desktop\Tesco test\Incomplete",filename+".pdf"))
