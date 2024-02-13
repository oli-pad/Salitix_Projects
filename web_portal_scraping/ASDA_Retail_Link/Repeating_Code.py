import os
import pyodbc
import pandas as pd
from Move_Retail_link_downloads import main


conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

cursor.execute("SELECT Salitix_client_number,salitix_client_name,user_name,password FROM [Salitix_Master_Data].[dbo].[salitix_retail_access_credentials] WHERE [system_name]='RETAIL LINK' OR [system_name]='Retail Link';")
User_List=cursor.fetchall()
User_List=pd.DataFrame(User_List)
print(User_List)

cursor.execute("SELECT * FROM [Salitix_Scrubbed_Data_Staging].[dbo].[Scrubbed_ASDA_Customer_Charges_Stg];")
ASDA_Charges=cursor.fetchall()
print(ASDA_Charges)
ASDA_Charges=pd.DataFrame(ASDA_Charges)

print(ASDA_Charges)

ASDA_Charges.to_excel(r'C:\Users\Python\Desktop\ASDA Images\Scrubbed_Charges\ASDA_Charges.xlsx')

main()

client_number = ASDA_Charges["Client_Number"].loc[0]
print(client_number)
client_login = User_List.loc[User_List[0]==client_number]

# for i in range(250):
#     os.system('python ASDA_Retail_link.py')
