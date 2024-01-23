import os
import pyodbc

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

cursor.execute("SELECT salitix_client_name,user_name,password FROM [Salitix_Master_Data].[dbo].[salitix_retail_access_credentials] WHERE [system_name]='Tesco Partners Toolkit';")
User_List=cursor.fetchall()
conn2 = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Pricing_Data_Formatted;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor2 = conn2.cursor()

generate_arg='python Download_Price_File.py {} {} {}'
for i in range(len(User_List)):
    os.system(generate_arg.format(User_List[i][1],User_List[i][2],User_List[i][0]))
