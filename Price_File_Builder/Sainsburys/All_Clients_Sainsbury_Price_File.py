import pyodbc
import os

folder_name={"BACARDI":"Bacardi","AB_INBEV":"Ab_Inbev","AG_BARR":"AG_Barr","BURTONS":"Burtons","COTY":"Coty","FINSBURY_FOODS":"Finsbury_Foods",
"HEINEKEN":"Heineken","KETTLE_FOODS":"Kettle_foods","KINNERTON":"Kinnerton","KP_SNACKS":"KP_Snacks","MAXXIUM":"Maxxium","PLADIS":"Pladis",
"PREMIER_FOODS":"Premier foods","TILDA":"Tilda","WEETABIX":"Weetabix","YOUNGS":"Youngs","PRINCES":"Princes","LOREAL":"Loreal"}

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_master_data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

cursor.execute("SELECT Salitix_client_number,Salitix_client_name FROM [Salitix_Master_Data].[dbo].[salitix_client_numbers];")
User_List=cursor.fetchall()
conn.close()

arg=r'python Sainsbury_Price_File_Builder.py "W:\Audit\{}\Documentation\Sainsbury_Salesforce\Price\CPC" "W:\Audit\{}\Documentation\Sainsbury_Salesforce\Price\NLF" "{}" {}"'

conn2 = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Pricing_Data_Formatted;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor2 = conn2.cursor()

conn3 = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Pricing_Data_Staging;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor3 = conn3.cursor()

for i in User_List:
    Salitix_client_number=i[0]
    Salitix_client_name=i[1]
    #try:
    if Salitix_client_number=="CL027":
        cursor3.execute("DELETE [Salitix_Pricing_Data_Staging].[dbo].[Pricing_Sainsburys_Stg];")
        cursor3.commit()
        os.system(arg.format(folder_name[Salitix_client_name],folder_name[Salitix_client_name],Salitix_client_number,Salitix_client_name))
        #insert exec into other code
        cursor2.execute("EXEC [Salitix_Pricing_Data_Formatted].[dbo].[prc_Pricing_Sainsburys_Ftd_Insert] 'SAINSBURY_PRICE_FILE_"+Salitix_client_name+".csv'")
        cursor2.commit()
    #except:
    #    print("Error with "+Salitix_client_name)

conn3.close()
conn2.close()
