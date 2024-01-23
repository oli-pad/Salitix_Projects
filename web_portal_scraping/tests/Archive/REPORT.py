import pyodbc

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_EPOS_Data_Formatted;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

#cursor.execute("SELECT Client_Name,Customer_Name,ScrubbedFile,FileStatus FROM [Salitix_EPOS_Data_Formatted].[dbo].[prc_Scrubbed_EPOS_File_Log_Insert]")
#User_List=cursor.fetchall()
#print(User_List)

#cursor.execute("INSERT [Salitix_EPOS_Data_Formatted].[dbo].[Scrubbed_EPOS_File_Log] ([Salitix_Client_Number],[Salitix_Customer_Number],[ScrubbedFile],[Status]) VALUES('Cl001','TES01','Tesco-Sales_and_stock-TPNB_Sales_x_store-2022Mar11 Bacardi.xlsx','TRUE');")
#cursor.commit()
#conn.close()
sql="DECLARE @RC int; EXEC @RC = [Salitix_EPOS_Data_Formatted].[dbo].[prc_Scrubbed_EPOS_File_Log_Insert] 'BACARDI','Tesco','TEST','True';SELECT @RC AS rc;"
cursor.execute(sql)
cursor.commit()
conn.close()
rc = cursor.fetchval()
print(rc)

#cursor.execute("SELECT salitix_client_name,user_name,password FROM [Salitix_Master_Data].[dbo].[salitix_retail_access_credentials] WHERE [system_name]='Tesco Partners Toolkit';")
#User_List=cursor.fetchall()
#print(User_List)
