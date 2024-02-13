import os
import pyodbc
from sys import argv

###This may need updating when changing where it is called###
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

cursor.execute("SELECT salitix_client_name,user_name,password FROM [Salitix_Master_Data].[dbo].[salitix_retail_access_credentials] WHERE [system_name]='Tesco Partners Toolkit';")
User_List=cursor.fetchall()
error_list=[]

generate_arg=r"python J:\Code\web_portal_scraping\Teco_Toolkit_Daily_EPOS\Daily_Tesco_EPOS_Generating.py {} {} ALL 200"

for i in range(len(User_List)):
    os.system(generate_arg.format("7","27"))
    