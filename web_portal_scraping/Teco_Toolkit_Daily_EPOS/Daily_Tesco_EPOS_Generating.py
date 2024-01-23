import os
import pyodbc
from sys import argv

script,number_of_days,start_num,client,index=argv

###This may need updating when changing where it is called###
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

cursor.execute("SELECT salitix_client_name,user_name,password FROM [Salitix_Master_Data].[dbo].[salitix_retail_access_credentials] WHERE [system_name]='Tesco Partners Toolkit';")
User_List=cursor.fetchall()
error_list=[]

generate_arg=r'python C:\Users\python\Desktop\projects\web_portal_scraping\Teco_Toolkit_Daily_EPOS\Tesco_EPOS_Portal_Generate.py {} {} {} {} {}'
if client=='ALL':
    for i in range(len(User_List)):
        os.system(generate_arg.format(User_List[i][0],User_List[i][1],User_List[i][2],number_of_days,start_num))
else:
    os.system(generate_arg.format(User_List[int(index)][0],User_List[int(index)][1],User_List[int(index)][2],number_of_days,start_num))