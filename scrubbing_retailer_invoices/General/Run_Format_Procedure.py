import pyodbc

# Path: scrubbing_retailer_invoices/General/Run_Format_Procedure.py

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

SQL_Query = "EXEC [Salitix_Scrubbed_Data_Formatted].[dbo].[Format_Scrubbed_Charges]"
print('Running "EXEC [Salitix_Scrubbed_Data_Formatted].[dbo].[Format_Scrubbed_Charges]"')
# 29/05 JR added print

cursor.execute(SQL_Query)
conn.commit()
conn.close()