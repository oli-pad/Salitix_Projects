import pyodbc
import os
import shutil
import pandas as pd
import csv

folder_name={"BACARDI":"Bacardi","AB_INBEV":"Ab_Inbev","AG_BARR":"AG_Barr","BURTONS":"Burtons","COTY":"Coty","FINSBURY_FOODS":"Finsbury_Foods",
"HEINEKEN":"Heineken","KETTLE_FOODS":"Kettle_foods","KINNERTON":"Kinnerton","KP_SNACKS":"KP_Snacks","MAXXIUM":"Maxxium","PLADIS":"Pladis",
"PREMIER_FOODS":"Premier foods","TILDA":"Tilda","WEETABIX":"Weetabix","YOUNGS":"Youngs","PRINCES":"Princes","LOREAL":"Loreal"}

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_master_data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

cursor.execute("SELECT Salitix_client_number,Salitix_client_name FROM [Salitix_Master_Data].[dbo].[salitix_client_numbers];")
User_List=cursor.fetchall()
conn.close()

arg=r'python Sainsbury_Price_File_Builder.py "W:\Audit\{}\Documentation\Sainsbury_Salesforce\Price\CPC" "W:\Audit\{}\Documentation\Sainsbury_Salesforce\Price\NLF" "{}" {}"'

promo_arg=r'python Sainsbury_promo_form.py "W:\Audit\{}\Documentation\Sainsbury_Salesforce\Promo Schedule\PRF" "W:\Audit\{}\Documentation\Sainsbury_Salesforce\Price" "W:\Audit\{}\Documentation\Sainsbury_Salesforce\Promo Schedule"'

conn2 = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Pricing_Data_Formatted;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor2 = conn2.cursor()

conn3 = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Pricing_Data_Staging;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor3 = conn3.cursor()

Client_Number = input("What Client Code do you want to run?   >")
while Client_Number not in [i[0] for i in User_List]:
    Client_Number = input("What Client Code do you want to run?   >")

def folders_exist(client_name):
    if not os.path.exists(r'W:\Audit\{}\Documentation\Sainsbury_Salesforce\Price\CPC'.format(client_name)):
        os.makedirs(r'W:\Audit\{}\Documentation\Sainsbury_Salesforce\Price\CPC'.format(client_name))
    if not os.path.exists(r'W:\Audit\{}\Documentation\Sainsbury_Salesforce\Price\NLF'.format(client_name)):
        os.makedirs(r'W:\Audit\{}\Documentation\Sainsbury_Salesforce\Price\NLF'.format(client_name))
    if not os.path.exists(r'W:\Audit\{}\Documentation\Sainsbury_Salesforce\Promo Schedule\PRF'.format(client_name)):
        os.makedirs(r'W:\Audit\{}\Documentation\Sainsbury_Salesforce\Promo Schedule\PRF'.format(client_name))

def Move_files(client_name,client_number):
    file_list  =  os.listdir(r'C:\Users\python\Downloads')
    PRF_files = [i for i in file_list if i.startswith('PRF')]
    NLF_files = [i for i in file_list if i.startswith('NLF')]
    CPC_files = [i for i in file_list if i.startswith('CPC')]
    folders_exist(client_name)
    for i in PRF_files:
        try:
            shutil.copy2(r'C:\Users\python\Downloads\{}'.format(i),
                        r'W:\Audit\{}\Documentation\Sainsbury_Salesforce\Promo Schedule\PRF\{}'.format(client_name, i))
            os.remove(r'C:\Users\python\Downloads\{}'.format(i))  # Delete the original file after successful copy
        except Exception as e:
            print("Error moving file:", e)  # Provide a more informative error message
    # Optionally, consider additional error handling or logging strategies here
    for i in NLF_files:
        try:
            shutil.copy2(r'C:\Users\python\Downloads\{}'.format(i),
                        r'W:\Audit\{}\Documentation\Sainsbury_Salesforce\Price\NLF\{}'.format(client_name, i))
            os.remove(r'C:\Users\python\Downloads\{}'.format(i))  # Delete the original file after successful copy
        except Exception as e:
            print("Error moving file:", e)  # Provide a more informative error message
    for i in CPC_files:
        try:
            shutil.copy2(r'C:\Users\python\Downloads\{}'.format(i),
                        r'W:\Audit\{}\Documentation\Sainsbury_Salesforce\Price\CPC\{}'.format(client_name, i))
            os.remove(r'C:\Users\python\Downloads\{}'.format(i))  # Delete the original file after successful copy
        except Exception as e:
            print("Error moving file:", e)  # Provide a more informative error message

        

for i in User_List:
    Salitix_client_number=i[0]
    Salitix_client_name=i[1]
    #try:
    if Salitix_client_number==Client_Number:
        Move_files(folder_name[Salitix_client_name],Salitix_client_number)
        cursor3.execute("DELETE [Salitix_Pricing_Data_Staging].[dbo].[Pricing_Sainsburys_Stg];")
        cursor3.commit()
        cursor2.execute("DELETE [Salitix_Pricing_Data_Formatted].[dbo].[Pricing_Sainsburys_Ftd] WHERE Salitix_client_number = '"+Salitix_client_number+"';")
        cursor2.commit()
        os.system(arg.format(folder_name[Salitix_client_name],folder_name[Salitix_client_name],Salitix_client_number,Salitix_client_name))
        #insert exec into other code
        cursor2.execute("EXEC [Salitix_Pricing_Data_Formatted].[dbo].[prc_Pricing_Sainsburys_Ftd_Insert] 'SAINSBURY_PRICE_FILE_"+Salitix_client_name+".csv'")
        cursor2.commit()

        rows = cursor2.execute("SELECT * FROM [Salitix_Pricing_Data_Formatted].[dbo].[Pricing_Sainsburys_Ftd] WHERE Salitix_client_number = '"+Salitix_client_number+"'")
        with open(r'W:\Audit\{}\Documentation\Sainsbury_Salesforce\Price\SAINSBURY_PRICE_FILE.csv'.format(folder_name[Salitix_client_name]), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([x[0] for x in cursor2.description])  # column headers
            for row in rows:
                writer.writerow(row)

        os.system(promo_arg.format(folder_name[Salitix_client_name],folder_name[Salitix_client_name],folder_name[Salitix_client_name]))
    #except:
    #    print("Error with "+Salitix_client_name)
    #    continue


conn3.close()
conn2.close()
