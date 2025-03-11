import os
import pyodbc
import pandas as pd
from Move_Retail_link_downloads import main
import csv
import time
import sys

script, start_date, end_date = sys.argv

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

rows = cursor.execute(f"SELECT * FROM [Salitix_Scrubbed_Data_Staging].[dbo].[Scrubbed_ASDA_Customer_Charges_Stg] WHERE SAL_Invoice_Type = 'PR' and Invoice_Date >= '{start_date}' and Invoice_Date <= '{end_date}';")
ASDA_Charges=cursor.fetchall()

with open(r'C:\Users\Python\Desktop\ASDA Images\Scrubbed_Charges\ASDA_Charges.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([x[0] for x in cursor.description])  # column headers
    for row in ASDA_Charges:
        writer.writerow(row)

main()

time.sleep(5)

ASDA_Charges=pd.read_csv(r'C:\Users\Python\Desktop\ASDA Images\Scrubbed_Charges\ASDA_Charges.csv')

client_number = ASDA_Charges["Salitix_client_number"].loc[0]

cursor.execute("SELECT Salitix_client_number,salitix_client_name,user_name,password FROM [Salitix_Master_Data].[dbo].[salitix_retail_access_credentials] WHERE ([system_name]='RETAIL LINK' OR [system_name]='Retail Link') and [Salitix_client_number] = '{}';".format(client_number.replace(" ", "")))

User_List=cursor.fetchall()

for i in range(50):
    print(f"Attempt {i+1} out of 50")
    os.system(r'python C:\Users\python\Desktop\projects\web_portal_scraping\ASDA_Retail_Link\ASDA_Retail_link.py "{}" "{}"'.format(User_List[0][2], User_List[0][3]))
