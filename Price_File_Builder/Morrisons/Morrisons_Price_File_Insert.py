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

price_file_path=r"Z:\Pricing"

Salitix_customer_number_0="MOR01"

cursor2.execute("DELETE [Sandbox].[dbo].[Pricing_Morrisons_Stg];")
cursor2.commit()

for i in os.listdir(price_file_path):
    if i[:1]=="M":
        df=pd.read_csv(os.path.join(price_file_path,i))
        Salitix_client_name_0=i.replace("MORRISONS_PRICE_FILE_","")
        print(Salitix_client_name_0)
        Salitix_client_name_0=Salitix_client_name_0.replace(".csv","")
        Salitix_client_number_0=[j[0] for j in User_List if Salitix_client_name_0==j[1]]
        print(Salitix_client_number_0)
        df=df.assign(SourceFile=[i for j in range(len(df))])
        df=df.assign(SourceInd=["R" for j in range(len(df))])
        df.insert(0,"Salitix_client_number",[Salitix_client_number_0[0] for j in range(len(df))])
        df.insert(1,"Salitix_customer_number",[Salitix_customer_number_0 for j in range(len(df))])
        cols = ",".join([str(i).replace(" ","_") for i in df.columns.tolist()])
        print(cols)
        for x,row in df.iterrows():
            row_info_0=[str(j).replace("'","") for j in row]
            for x in range(len(row_info_0)):
                if row_info_0[x]=="nan":row_info_0[x]="NULL"
            row_info_0[0]="'"+row_info_0[0]+"'"
            row_info_0[1]="'"+row_info_0[1]+"'"
            row_info_0[2]="'"+row_info_0[2][6:]+"-"+row_info_0[2][3:5]+"-"+row_info_0[2][:2]+"'"
            row_info_0[3]="'"+row_info_0[3]+"'"
            row_info_0[9]="'"+row_info_0[9]+"'"
            row_info_0[10]="'"+row_info_0[10]+"'"
            row_info_0[11]="'"+row_info_0[11]+"'"
            row_info_0[12]="'"+row_info_0[12]+"'"
            row_info_0[13]="'"+row_info_0[13]+"'"
            row_info_0[14]="'"+row_info_0[14]+"'"
            row_info=",".join([j for j in row_info_0])
            sql1 = "INSERT INTO [Sandbox].[dbo].[Pricing_Morrisons_Stg] (" +cols + ") VALUES ("+row_info+");"
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
