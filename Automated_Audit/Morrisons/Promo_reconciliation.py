import pyodbc
import pandas as pd
import os
from EPOS_Discrepency import EPOS_Discrepency
from Incorrect_Trigger import Incorrect_Trigger
from Duplicate_Invoices import Duplicate_Invoices
from Duplicate_Funding import Duplicate_Funding

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

#For User Input
Client_Code=input("What's the Client Code?  >")
Retailer_Code=input("What's the Retailer Code?  >")
Date_period_1=input("Start date?  >")
Date_period_2=input("End date?  >")
#To store the name of the databse for the relevant client.
cursor.execute("SELECT Salitix_client_number,Salitix_client_name,Db FROM [Salitix_Master_Data].[dbo].[salitix_client_numbers] WHERE Salitix_client_number='"+Client_Code+"';")
User_List=cursor.fetchall()
Client_Db=User_List[0][2]

#To connect to sales invoices in the database
SI_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE='+Client_Db+';Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
SI_cursor = SI_conn.cursor()

#To store the sales invoices in the order in which is required for claims.
SI_query="SELECT order_number,invoice_number,pricing_date,billing_date,Retailer_Primary_Product_Number,Vendor_Primary_Product_Number,product_description,units_per_case,qty,unit_price,line_goods_value FROM ["+Client_Db+"].[dbo].[vw_SAL_Sales_Invoice_Detail] WHERE salitix_customer_number='"+Retailer_Code+"'AND Retailer_Primary_Product_Number='{}' AND pricing_date BETWEEN '{}' AND '{}';"

#To connect to the new Promo Schedules.
PS_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Sandbox;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
PS_cursor = PS_conn.cursor()

#To store the promo schedule for a specific client between a allocated period.
PS_query="SELECT * FROM [Sandbox].[dbo].[Promotions_Morrisons_Stg] WHERE salitix_client_number='"+Client_Code+"' AND Start_Date BETWEEN '"+Date_period_1+"' AND '"+Date_period_2+"' ORDER BY Start_Date;"
Promo_Schedule_df=pd.read_sql(PS_query,PS_conn)

#To store customer charges until IA finishes processing.
Customer_Charges_df=pd.read_csv(os.path.join(r"C:\Users\Python\Desktop\Morrisons Analysis Project\Customer_Charges",Client_Code+"_Customer_Charges.csv"))
Customer_Charges_df['Start_Date'] = pd.to_datetime(Customer_Charges_df['Start_Date'], format='%d/%m/%Y')
Customer_Charges_df['End_Date'] = pd.to_datetime(Customer_Charges_df['End_Date'], format='%d/%m/%Y')

#To connect to the EPOS database.
EPOS_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_EPOS_Data_Formatted;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
#EPOS_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Sandbox;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
EPOS_cursor = EPOS_conn.cursor()

#To store EPOS data.
EPOS_query="SELECT * FROM ["+Client_Db+"].[dbo].[EPOS] WHERE Retailer_Product_Number='{}' AND Calendar_Date BETWEEN '{}' AND '{}';"

#To store the product file.
Product_File_df = pd.read_csv(os.path.join(r"C:\Users\Python\Desktop\Morrisons Analysis Project\Product_Files",Client_Code+"_Product_File.csv"))

#EPOS_Discrepency(Promo_Schedule_df,Product_File_df,Customer_Charges_df,EPOS_conn,EPOS_query,Client_Code)
Incorrect_Trigger(Promo_Schedule_df,Product_File_df,Customer_Charges_df,EPOS_conn,EPOS_query,Client_Code)
Duplicate_Invoices(Product_File_df,Customer_Charges_df,Client_Code)
Duplicate_Funding(Promo_Schedule_df,Product_File_df,Customer_Charges_df,SI_conn,SI_query,Client_Code)
