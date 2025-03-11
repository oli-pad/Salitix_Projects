import pyodbc

import sys

script,client,retailer = sys.argv

# Path: scrubbing_retailer_invoices/General/Run_Format_Procedure.py

Client_code_dic={'Ab_Inbev':"CL023", 'AG_Barr':"CL005", 'Bacardi':"CL001",
    'Burtons':"CL003", 'Coty':"CL027",'Finsbury_Foods':"CL014",
    'Foxs':"CL999", 'Heineken':"CL028", 'Kettle Foods':"CL026", 
    'Kinnerton':"CL022", 'Maxxium':"CL012", 'Pladis':"CL002", 
    'Premier_Foods':"CL020", 'Princes':"CL029", 'Tilda':"CL013", 'Youngs':"CL004",
    'Loreal':'CL031'}
Retailer_Code_dic={'Tesco':"TES01", 'ASDA':"ASD01", 'Sainsbury':"SAI01", 'Morrisons':"MOR01"}

Salitix_Client_Number=Client_code_dic[client]
Salitix_Customer_Number=Retailer_Code_dic[retailer]

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

SQL_Query = f"EXEC [Salitix_Master_Data].[dbo].[prc_Run_SCC_Load_Scrubbed_Customer_Charges_DTL] {Salitix_Client_Number}, {Salitix_Customer_Number}"

cursor.execute(SQL_Query)
conn.commit()
conn.close()