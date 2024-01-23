import pyodbc
import pandas as pd
import os
from Participation_EPOS import Participation_EPOS
from Incorrect_Trigger import Incorrect_Trigger
from Duplicate_Invoices import Duplicate_Invoices
from Duplicate_Funding import Duplicate_Funding
from Trigger_Trend import Trigger_Trend
from EPOS_Discrepancy import EPOS_Discrepency

from sys import argv

script,Client_Code,Retailer_Code,Date_period_1,Date_period_2,SCC_alt=argv

def get_audit_year(start,end,year_list,compare):
    for i in range(len(year_list)-1):
        start_date=str(start).replace(str(1900),str(year_list[i]))
        end_date=str(end).replace(str(1901),str(year_list[i+1]))
        compare=compare[0:].replace("'","")
        if compare>=start_date:
            if compare<=end_date:
                return "'"+str(year_list[i])+"'"
            else:continue
        else:continue
    return "'"+compare[0:4]+"'"


conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

PS_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Sandbox;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
PS_cursor = PS_conn.cursor()


cursor.execute("SELECT Salitix_client_number,Salitix_client_name,Db FROM [Salitix_Master_Data].[dbo].[salitix_client_numbers] WHERE Salitix_client_number='"+Client_Code+"';")
User_List=cursor.fetchall()
Client_Db=User_List[0][2]
cursor.execute("SELECT salitix_customer_number,salitix_Customer_FY_StartDate,salitix_Customer_FY_EndDate FROM [Salitix_Master_Data].[dbo].[salitix_customer_numbers] WHERE Salitix_customer_number='"+Retailer_Code+"';")
Retailer_List=cursor.fetchall()
Retailer_Start=Retailer_List[0][1]
Retailer_End=Retailer_List[0][2]
Years=[2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026,2027]

#To connect to sales invoices in the database
SI_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE='+Client_Db+';Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
SI_cursor = SI_conn.cursor()

#To store the sales invoices in the order in which is required for claims.
SI_query="SELECT order_number,invoice_number,pricing_date,billing_date,Retailer_Primary_Product_Number,Vendor_Primary_Product_Number,product_description,units_per_case,qty,unit_price,line_goods_value FROM ["+Client_Db+"].[dbo].[vw_SAL_Sales_Invoice_Detail] WHERE salitix_customer_number='"+Retailer_Code+"'AND line_goods_value>0 AND unit_price>0 AND Retailer_Primary_Product_Number='{}' AND pricing_date BETWEEN '{}' AND '{}' ORDER BY pricing_date;"

if SCC_alt=="Y":
    Customer_Charges_Query="SELECT * FROM ["+Client_Db+"].[dbo].[vw_SAL_Customer_Charges_Alt] WHERE Salitix_Customer_Number='"+Retailer_Code+"' AND CC_HDR_ID in (SELECT CC_HDR_ID FROM ["+Client_Db+"].[dbo].[vw_SAL_Customer_Charges_Alt] GROUP BY [CC_HDR_ID] HAVING (ABS(SUM([Line_Level_Net]) - MIN([Nett_Amount]))<=10) OR (ABS(SUM([Line_Level_Net]) -(MIN([Gross_Amount]) - MIN([VAT])))<=10))"
    Customer_Charges_df=pd.read_sql(Customer_Charges_Query,SI_conn)
    Customer_Charges_df.rename(columns = {"Salitix_Customer_Number": "Salitix_customer_number"}, inplace = True)
    Customer_Charges_df.rename(columns = {"Retailer_Invoice": "Invoice_No"}, inplace = True)
    Customer_Charges_df.rename(columns = {"Retailer_Product_Number":"Product_No"}, inplace = True)
    Customer_Charges_df.rename(columns = {"Unit_Funding":"Unit_Price"}, inplace = True)
    Customer_Charges_df.rename(columns = {"Units": "Quantity"}, inplace = True)
    Customer_Charges_df.rename(columns = {"Line_Level_Net": "Net_Amount"}, inplace = True)
    Customer_Charges_df.rename(columns = {"Promotion_ID": "Promotion_No"}, inplace = True)
elif SCC_alt=="N":
    CC_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Scrubbed_Data_Formatted;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
    CC_cursor = CC_conn.cursor()
    CC_Query="SELECT * FROM [Salitix_Scrubbed_Data_Formatted].[dbo].[Scrubbed_Customer_Charges_Ftd] WHERE Salitix_customer_number='"+Retailer_Code+"' AND Salitix_client_number ='"+Client_Code+"'"
    Customer_Charges_df=pd.read_sql(CC_Query,CC_conn)

if Retailer_Code=="TES01":
    PS_query="SELECT * FROM ["+Client_Db+"].[dbo].[vw_salitix_promotions_pz_Merged] WHERE salitix_customer_number='"+Retailer_Code+"' AND Instore_Start_Date BETWEEN '"+Date_period_1+"' AND '"+Date_period_2+"';"
    Promo_Schedule_df=pd.read_sql(PS_query,SI_conn)
elif Retailer_Code=="SUP01" or Client_Code=='CL027':
    Promo_Schedule_df=pd.DataFrame()
else:
    PS_query="SELECT * FROM ["+Client_Db+"].[dbo].[vw_salitix_promotions_scratch_table] WHERE salitix_customer_number='"+Retailer_Code+"' AND Instore_Start_Date BETWEEN '"+Date_period_1+"' AND '"+Date_period_2+"';"
    Promo_Schedule_df=pd.read_sql(PS_query,SI_conn)

#connecting to the EPOS in SQL server.
EPOS_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_EPOS_Data_Formatted;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
EPOS_cursor = EPOS_conn.cursor()                                                                                                                                            #AND Calendar_Date BETWEEN '"+Date_period_1+"' AND '"+Date_period_2+"'  

EPOS_query="SELECT * FROM [Salitix_EPOS_Data_Formatted].[dbo].[Salitix_EPOS_ftd] WHERE salitix_client_number='"+Client_Code+"' AND salitix_customer_number='"+Retailer_Code+"' AND Retailer_Product_Number='{}' AND Calendar_Date BETWEEN '{}' AND '{}';"

Full_Exceptions_Report=[]

Exceptions_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Claims_Database;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = Exceptions_conn.cursor()

ACR_Ftd = "SELECT * FROM [Salitix_Claims_Database].[dbo].[ACR_Automated_Claim_Report_Ftd] WHERE Client_Code='"+Client_Code+"' AND Customer_Code='"+Retailer_Code+"';"
ACR_Ftd_df=pd.read_sql(ACR_Ftd,Exceptions_conn)
# print(ACR_Ftd_df)

def Duplicate_Check(row,table):
    table = table[table["Claim_Category"]==row[1].replace("'","")]
    table = table[table["Product_No"]==row[3].replace("'","")]
    Invoice_List=table["Invoice_List"].tolist()
    row_invoice_list=row[-1].split(",")
    #check all rows in the table
    for j in Invoice_List:
        j=j.split(",")
        for i in row_invoice_list:
            #if the invoice is in the table row then check the next invoice in the row
            if i.replace("'","") not in j:
                break
            return True,table
    df=pd.concat([ACR_Ftd_df,pd.Series(row+[Client_Code,Retailer_Code,'20000','Test','Test','Test','Test'])], ignore_index=True)
    return False,df

if SCC_alt=='Y':
    for i in Customer_Charges_df.index:
        if pd.isna(Customer_Charges_df.loc[i,"Start_Date"]):
            Customer_Charges_df.loc[i,"Start_Date"]=Customer_Charges_df.loc[i,"Document_Date"]
        if pd.isna(Customer_Charges_df.loc[i,"End_Date"]):
            Customer_Charges_df.loc[i,"End_Date"]=Customer_Charges_df.loc[i,"Document_Date"]
        if pd.isna(Customer_Charges_df.loc[i,"ImageInvoice"]):
            continue
        else:  
            Customer_Charges_df.at[i,"Invoice_No"]=Customer_Charges_df.loc[i,"ImageInvoice"].replace(" ","")
            
# for i in EPOS_Discrepency(Client_Code,Retailer_Code,Promo_Schedule_df,Customer_Charges_df):
#     status,ACR_Ftd_df=Duplicate_Check(i,ACR_Ftd_df)
#     if status==False:Full_Exceptions_Report.append(i)
for i in Incorrect_Trigger(Promo_Schedule_df,Customer_Charges_df,EPOS_conn,EPOS_query,Client_Code,Retailer_Code):
    status,ACR_Ftd_df=Duplicate_Check(i,ACR_Ftd_df)
    if status==False:Full_Exceptions_Report.append(i)
for i in Duplicate_Invoices(Customer_Charges_df,Client_Code,Retailer_Code,EPOS_conn,EPOS_query,Promo_Schedule_df):
    status,ACR_Ftd_df=Duplicate_Check(i,ACR_Ftd_df)
    if status==False:Full_Exceptions_Report.append(i)
for i in Duplicate_Funding(Promo_Schedule_df, Customer_Charges_df, SI_conn, SI_query, Client_Code, Retailer_Code, EPOS_conn, EPOS_query):
    try: status, ACR_Ftd_df = Duplicate_Check(i, ACR_Ftd_df)
    except: status=True
    if status == False:Full_Exceptions_Report.append(i)
#Full_Exceptions_Report.append(Trigger_Trend(Promo_Schedule_df,Customer_Charges_df,EPOS_conn,EPOS_query,Client_Code,Retailer_Code)

def insert_into_table(list):
    print("Exceptions",list)
    if list==[None]:return
    cols="Reviewed_Status,Claim_Category,Period,Product_No,Potential_Value,EPOS_Start_Date,EPOS_End_Date,Promo_Start_Date,Promo_End_Date,SI_Start_Date,SI_End_Date,Evidence_File_Path,Promo_Schedule_Promo_ID,Invoice_List,Client_Code,Customer_Code,Audit_Year"
    for i in list:
        if float(i[4].replace("'",""))<500:continue
        row_info=",".join([str(j) for j in i])
        Audit_Year=get_audit_year(Retailer_Start,Retailer_End,Years,i[5])
        sql1 = "INSERT INTO [Salitix_Claims_Database].[dbo].[ACR_Automated_Claim_Report_Stg] (" +cols + ") VALUES ("+row_info+",'"+Client_Code+"','"+Retailer_Code+"',"+Audit_Year+");"
        try:
            cursor.execute(sql1)
            cursor.commit()
        except:
            print("Error ", sql1)
    sql2 = "EXEC [Salitix_Claims_Database].[dbo].[prc_ACR_Formatting]"
    cursor.execute(sql2)
    cursor.commit()
    Exceptions_conn.close()

# #duplicate check and remove
# df = pd.DataFrame(Full_Exceptions_Report)
# df.to_csv()
insert_into_table(Full_Exceptions_Report)