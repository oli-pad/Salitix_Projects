import os
from pathlib import Path
import pandas as pd
from collections import namedtuple
import numpy as np
from sys import argv
import pyodbc

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()
sql="SELECT Salitix_client_number,Salitix_client_name FROM [Salitix_Master_Data].[dbo].[salitix_client_numbers]"
cursor.execute(sql)
User_List=cursor.fetchall()
print(User_List)

conn2 = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Sandbox;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor2 = conn2.cursor()

conn3 = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Sandbox;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor3 = conn3.cursor()

promo_schedule_path=r"Z:\Promotions\Scraped Promotions"

Salitix_customer_number_0="SAI01"

cursor2.execute("DELETE [Sandbox].[dbo].[Promotions_Sainsbury_Stg];")
cursor2.commit()

for i in os.listdir(promo_schedule_path):
    if i[:2]=="SA":
        print(os.path.join(promo_schedule_path,i))
        df=pd.read_csv(os.path.join(promo_schedule_path,i))
        Salitix_client_name_0=i.replace("SAINSBURY_PROMO_SCHEDULE_","")
        print(Salitix_client_name_0)
        Salitix_client_name_0=Salitix_client_name_0.replace(".csv","")
        Salitix_client_number_0=[j[0] for j in User_List if Salitix_client_name_0==j[1]]
        print(Salitix_client_number_0)
        cols = ",".join([str(i).replace(" ","_") for i in df.columns.tolist()])
        print(cols)
        for x,row in df.iterrows():
            row_info_0=[str(j).replace("'","") for j in row]
            for x in range(len(row_info_0)):
                if row_info_0[x]=="nan":row_info_0[x]="NULL"
            row_info_0[0]="'"+row_info_0[0]+"'"
            row_info_0[1]="'"+row_info_0[1]+"'"
            row_info_0[5]="'"+row_info_0[5].replace(".0","")+"'"
            row_info_0[3]="'"+row_info_0[3][6:]+"-"+row_info_0[3][3:5]+"-"+row_info_0[3][:2]+"'"
            row_info_0[4]="'"+row_info_0[4][6:]+"-"+row_info_0[4][3:5]+"-"+row_info_0[4][:2]+"'"
            row_info_0[2]="'"+row_info_0[2]+"'"
            row_info_0[6]="'"+row_info_0[6]+"'"
            row_info_0[7]="'"+row_info_0[7]+"'"
            row_info_0[10]="'"+row_info_0[10]+"'"
            row_info_0[11]="'"+row_info_0[11]+"'"
            row_info=",".join([j for j in row_info_0])
            print(row_info)
            sql1 = "INSERT INTO [Sandbox].[dbo].[Promotions_Sainsbury_Stg] (" +cols + ") VALUES ("+row_info+");"
            cursor3.execute(sql1)
            cursor3.commit()
            #except:print(row_info)
        #cursor2.execute("EXEC [Salitix_Pricing_Data_Formatted].[dbo].[prc_Pricing_Tesco_Ftd_Insert] '"+i+"'")
        #cursor2.commit()
        #cursor3.execute("DELETE [Salitix_Pricing_Data_Staging].[dbo].[Pricing_Tesco_Stg];")
        #cursor3.commit()
        #insert exec into other code

conn3.close()
conn2.close()
