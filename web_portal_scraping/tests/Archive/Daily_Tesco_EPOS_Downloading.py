import os
import pyodbc
from datetime import date
from datetime import timedelta
from collections import namedtuple
import pandas as pd
folder_name={"BACARDI":"Bacardi","AB_Inbev":"Ab_Inbev","AG_BARR":"AG_Barr","BURTONS":"Burtons","COTY":"Coty","FINSBURY_FOODS":"Finsbury_Foods",
"HEINEKEN":"Heineken","KETTLE_FOODS":"Kettle_foods","KINNERTON":"Kinnerton","KP_SNACKS":"KP_Snacks","MAXXIUM":"Maxxium","PLADIS":"Pladis",
"PREMIER_FOODS":"Premier_foods","TILDA":"Tilda","WEETABIX":"Weetabix","YOUNGS":"Youngs"}
days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
months={'01':"January","02":"February","03":"March","04":"April","05":"May","06":"June","07":"July","08":"August","09":"September","10":"October","11":"November","12":"Decemeber"}
short_months={"January":"Jan","February":"Feb","March":"Mar","April":"Apr","May":"May","June":"Jun","July":"Jul","August":"Aug","September":"Sep","October":"Oct","November":"Nov","Decemeber":"Dec"}

Line = namedtuple('Line',"File_Name Status")
report=[]

###This may need updating when changing where it is called###
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

cursor.execute("SELECT salitix_client_name,user_name,password FROM [Salitix_Master_Data].[dbo].[salitix_retail_access_credentials] WHERE [system_name]='Tesco Partners Toolkit';")
User_List=cursor.fetchall()
conn.close()

generate_arg='python Tesco_EPOS_Portal_Generate.py {} {} {} {}'
download_arg='python Tesco_EPOS_Portal_Download.py {} {} {} {}'

def dates_for_download(n,client):
    date_list=[]
    download_list=[]
    today = date.today()-timedelta(3)
    for i in range(n):
        Dates=today-timedelta(1+i)
        date_one = Dates.strftime("%d/%m/%Y")
        day=Dates.weekday()
        if date_one[0] == "0":
            date_list.append([date_one[1],months[date_one[3:5]],date_one[6:],days[day]])
        else:
            date_list.append([date_one[:2],months[date_one[3:5]],date_one[6:],days[day]])
            for j in date_list:
                download_list.append('Tesco-Sales_and_stock-TPNB_Sales_x_store-'+str(j[2])+short_months[j[1]]+str(j[0])+" "+folder_name[client]+".xlsx")
                return date_list,download_list

today=["PREMIER_FOODS","MAXXIUM","KETTLE_FOODS"]

def download():
    for i in range(len(User_List)):
        if User_List[i][0] in today:
            os.system(download_arg.format(User_List[i][0],User_List[i][1],User_List[i][2],14))

def expected_check_list():
    for i in range(len(User_List)):
        dates,download_check_list=dates_for_download(1,User_List[i][0])
        for j in download_check_list:
            expected_downloads.append(j)

def downloaded_check_list():
    rename_path="Z:\{}\EPOS Store\Tesco\Daily"
    for i in range(len(User_List)):
        for j in dir_contents(rename_path.format(folder_name[User_List[i][0]])):
            actual_downloads.append(j)

def dir_contents(path):
    file_list=[]
    for root, directories, files in os.walk(path):
        for filename in files:
            file_list.append(filename)
    return file_list

def Client_Retailer(n):
    Client=[]
    Retailer=[]
    for i in len(range(User_List)):
        for j in len(range(n)):
            Client.append(User_List[i][0])
            Retailer.append("Tesco")
    return Client,Retailer

def exceptions_report(expected_downloads,actual_downloads):
    Client,Retailer=Client_Retailer(14)
    count=0
    for i in expected_downloads:
        conn2 = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_EPOS_Data_Formatted;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
        cursor2 = conn2.cursor()
        if i in actual_downloads:
            report.append(Line(i,"True"))
            cursor2.execute("EXEC [Salitix_EPOS_Data_Formatted].[dbo].[prc_Scrubbed_EPOS_File_Log_Insert] "+Client[count]+",'Tesco',"+i+",'True'")
            cursor2.commit()
            conn2.close()
        else:
            report.append(Line(i,"False"))
            cursor2.execute("EXEC [Salitix_EPOS_Data_Formatted].[dbo].[prc_Scrubbed_EPOS_File_Log_Insert] "+Client[count]+",'Tesco',"+i+",'False'")
            cursor2.commit()
            conn2.close()
        count+=1
    df=pd.DataFrame(report)
    df.to_csv('Exception_Reports/exceptions {}.csv'.format(date.today().strftime("%d_%m_%Y")),index=False)



#read the folders and see if it has been fully Successful
download()
expected_downloads=[]
actual_downloads=[]
expected_check_list()
downloaded_check_list()
exceptions_report(expected_downloads,actual_downloads)
