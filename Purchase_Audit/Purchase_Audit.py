import pyodbc
from sys import argv

script,Client_Code=argv

# Connect to the database
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

cursor.execute("SELECT Salitix_client_number,Salitix_client_name,Db FROM [Salitix_Master_Data].[dbo].[salitix_client_numbers] WHERE Salitix_client_number='"+Client_Code+"';")
User_List=cursor.fetchall()
Client_Db=User_List[0][2]

client_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE='+Client_Db+';Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
client_cursor = client_conn.cursor()

