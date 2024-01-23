import os
import pyodbc

###This may need updating when changing where it is called###
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

cursor.execute("SELECT salitix_client_name,user_name,password FROM [Salitix_Master_Data].[dbo].[salitix_retail_access_credentials] WHERE [system_name]='Tesco Partners Toolkit';")
User_List=cursor.fetchall()

generate_arg='python Tesco_EPOS_Portal_Generate.py {} {} {} {}'
download_arg='python Tesco_EPOS_Portal_Download.py {} {} {} {}'

today=["PREMIER_FOODS","MAXXIUM","KETTLE_FOODS"]

for i in range(len(User_List)):
    if User_List[i][0] in today:
        os.system(generate_arg.format(User_List[i][0],User_List[i][1],User_List[i][2],14))
