import csv
import pandas as pd
import os
from sys import argv

def CSV_to_Excels():
    for i in dir_contents(r"C:\Users\Python\Desktop\Extras"):
        print(i)
        df=pd.read_csv(os.path.join(r"C:\Users\Python\Desktop\Extras",i),sep=";")
        print(df)
        df.to_excel(os.path.join(r"C:\Users\Python\Desktop\Extras",i.replace(".csv",".xlsx")),sheet_name='Store Level LDI',index=False)
        #os.remove(os.path.join(r"C:\Users\Python\Desktop\Extras",i))

def dir_contents(path):
    file_list=[]
    for root, directories, files in os.walk(path):
        for filename in files:
            file_list.append(filename)
    return file_list

CSV_to_Excels()
