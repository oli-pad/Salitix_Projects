import os
import pyodbc

###This may need updating when changing where it is called###
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

cursor.execute("SELECT salitix_client_name,user_name,password FROM [Salitix_Master_Data].[dbo].[salitix_retail_access_credentials] WHERE [system_name]='Tesco Partners Toolkit';")
User_List=cursor.fetchall()

generate_arg='python Tesco_EPOS_Portal_Generate.py {} {} {} {}'
download_arg='python Tesco_EPOS_Portal_Download.py {} {} {} {}'

for i in range(len(User_List)):
    os.system(generate_arg.format(User_List[i][0],User_List[i][1],User_List[i][2],1))
    print("Error with "+User_List[i][0])
