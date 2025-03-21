import os
import pyodbc
import pandas as pd
# importing sys
import sys
from sys import argv

script,client,retailer = argv

Client_code_dic={'Ab_Inbev':"CL023", 'AG_Barr':"CL005", 'Bacardi':"CL001",
    'Burtons':"CL003", 'Coty':"CL027",'Finsbury_Foods':"CL014",
    'Foxs':"CL999", 'Heineken':"CL028", 'Kettle Foods':"CL026", 
    'Kinnerton':"CL022", 'Maxxium':"CL012", 'Pladis':"CL002", 
    'Premier_Foods':"CL020", 'Princes':"CL029", 'Tilda':"CL013", 'Youngs':"CL004",
    'Loreal':'CL031'}
Retailer_Code_dic={'Tesco':"TES01", 'ASDA':"ASD01", 'Sainsbury':"SAI01", 'Morrisons':"MOR01"}
# 19/04 JR Changed 'Sainsburys' to 'Sainsbury' in Retailer_Code_dic because that's the actual name of the retailer in the flask form
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

CC_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Scrubbed_Data_Formatted;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
CC_cursor = CC_conn.cursor()

if client=="manual":
    Client_Code=input("What's the Client Code?  >")
    Retailer_Code=input("What's the Retailer Code?  >")
    cursor.execute("SELECT Salitix_client_number,Salitix_client_name,Db FROM [Salitix_Master_Data].[dbo].[salitix_client_numbers] WHERE Salitix_client_number='"+Client_Code+"';")
    User_List=cursor.fetchall()
    Client_Db=User_List[0][2]
else:
    # print(client,retailer)
    # print(Retailer_Code_dic)
    Client_Code=Client_code_dic[client]
    Retailer_Code=Retailer_Code_dic[retailer]
    cursor.execute("SELECT Salitix_client_number,Salitix_client_name,Db FROM [Salitix_Master_Data].[dbo].[salitix_client_numbers] WHERE Salitix_client_number='"+Client_Code+"';")
    User_List=cursor.fetchall()
    print(User_List)
    Client_Db=User_List[0][2]

Client_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE='+Client_Db+';Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
Client_cursor = Client_conn.cursor()

HDR_Query = "SELECT Vendor_Name,Retailer_Invoice FROM ["+Client_Db+"].[dbo].[SAL_Customer_Charges_HDR_Alt] GROUP BY Vendor_Name,Retailer_Invoice"
HDR_Charges_df=pd.read_sql(HDR_Query,Client_conn)
HDR_list=HDR_Charges_df["Retailer_Invoice"].tolist()

CC_Query="SELECT Invoice_No FROM [Salitix_Scrubbed_Data_Formatted].[dbo].[Scrubbed_Customer_Charges_Ftd] WHERE Salitix_customer_number='"+Retailer_Code+"' AND Salitix_client_number ='"+Client_Code+"' GROUP BY Invoice_No"
Customer_Charges_df=pd.read_sql(CC_Query,CC_conn)
CC_list=Customer_Charges_df["Invoice_No"].tolist()

CC_all_Query="SELECT * FROM [Salitix_Scrubbed_Data_Formatted].[dbo].[Scrubbed_Customer_Charges_Ftd] WHERE Salitix_customer_number='"+Retailer_Code+"' AND Salitix_client_number ='"+Client_Code+"'"
Customer_Charges_all_df=pd.read_sql(CC_all_Query,CC_conn)

def update(HDR_No,Inv_No):
    update_Query="UPDATE [Salitix_Scrubbed_Data_Formatted].[dbo].[Scrubbed_Customer_Charges_Ftd] SET HDR_Invoice_Number = '"+HDR_No+"' WHERE Invoice_No = '"+Inv_No+"';"
    CC_cursor.execute(update_Query)
    CC_cursor.commit()


for i in HDR_list:
    print(i)
    if i in CC_list:
        continue
    if Retailer_Code=="TES01":
        if "100"+i in CC_list:
            update(i,"100"+i)
        if "1002"+i in CC_list:
            update(i,"1002"+i)
        if "10021"+i in CC_list:
            update(i,"10021"+i)    
    elif Retailer_Code=="ASD01":
        if i[:10] in CC_list:
            update(i,i[:10])
        if i.replace("P-","") in CC_list:
            update(i,i.replace("P-",""))
    elif Retailer_Code=="SAI01":
        i_replace_new=i.replace(" _ ","-")
        if i_replace_new in CC_list:
            update(i,i_replace_new)
        i_replace_new1=i.replace(" _ ","_")
        if i_replace_new1 in CC_list:
            update(i,i_replace_new1)
        i_replace=i.replace("/","_")
        if i_replace in CC_list:
            update(i,i_replace)
        i_replace2=i_replace.replace("/","_")
        if i_replace2 in CC_list:
            update(i,i_replace2)
        i_replace3=i_replace.replace("/","")
        if i_replace3 in CC_list:
            update(i,i_replace3)
        i_replace4=i.replace("/"," _ ")
        if i_replace4 in CC_list:
            update(i,i_replace4)
        i_replace5=i.replace("-","_")
        if i_replace5 in CC_list:
            update(i,i_replace5)
        i_replace6=i_replace5.replace("-","_")
        if i_replace6 in CC_list:
            update(i,i_replace6)
        i_replace7=i.replace("-"," _ ")
        if i_replace7 in CC_list:
            update(i,i_replace7)
        i_replace8=i_replace5.replace("/","")
        if i_replace8 in CC_list:
            update(i,i_replace8)
        if Client_Code=='CL029':
            i_replace5="RP"+i.replace("/","_P0175_")
            print(i_replace5)
            if i_replace5 in CC_list:
                update(i,i_replace5)
        if Client_Code=='CL020':
            i_replace=i.replace("/","_P0819_")
            if i_replace in CC_list:
                update(i,i_replace)
            i_replace=i.replace("/","_M0587_")
            if i_replace in CC_list:
                update(i,i_replace)
    elif Retailer_Code=="MOR01":
        if "2017"+i[4:] in CC_list:
            update(i,"2017"+i[4:])
        if "2018"+i[4:] in CC_list:
            update(i,"2018"+i[4:])
        if "2019"+i[4:] in CC_list:
            update(i,"2019"+i[4:])
        if "2020"+i[4:] in CC_list:
            update(i,"2020"+i[4:])
        if "2021"+i[4:] in CC_list:
            update(i,"2021"+i[4:])
        if "2022"+i[4:] in CC_list:
            update(i,"2022"+i[4:])
        if "2023"+i[4:] in CC_list:
            update(i,"2023"+i[4:])
        if "2024"+i[4:] in CC_list:
            update(i,"2024"+i[4:])
        if "2025"+i[4:] in CC_list:
            update(i,"2025"+i[4:])
        if "2026"+i[4:] in CC_list:
            update(i,"2026"+i[4:])
        if "2017"+i in CC_list:
            update(i,"2017"+i)
        if "2018"+i in CC_list:
            update(i,"2018"+i)
        if "2019"+i in CC_list:
            update(i,"2019"+i)
        if "2020"+i in CC_list:
            update(i,"2020"+i)
        if "2021"+i in CC_list:
            update(i,"2021"+i)
        if "2022"+i in CC_list:
            update(i,"2022"+i)
        if "2023"+i in CC_list:
            update(i,"2023"+i)
        if "2024"+i in CC_list:
            update(i,"2024"+i)
        if "2025"+i in CC_list:
            update(i,"2025"+i)
        if "2026"+i in CC_list:
            update(i,"2026"+i)
        if i.replace("_","") in CC_list:
            update(i,i.replace("_",""))
        if "DEAL" in i or "." in i:
            deal_no=i.replace("DEAL","")
            string_split=deal_no.split()
            promotion_no=string_split[0]
            if i=='DEAL71365636 09.01.21':
                print(promotion_no)
            if len(i)>10:
                date=i[-8:]
                Invoice_date=date[:2]+"/"+date[3:5]+"/20"+date[6:8]
                Invoice_dash_date="20"+date[6:8]+"-"+date[3:5]+"-"+date[:2]
                Promo_df=Customer_Charges_all_df.loc[Customer_Charges_all_df["Promotion_No"]==promotion_no]
                Promo_Date_df=Promo_df.loc[Promo_df["Invoice_Date"]==Invoice_date]
                invoice_list=Promo_Date_df["Invoice_No"].unique()
                if i=='DEAL71365636 09.01.21':
                    print(Promo_df["Invoice_Date"])
                    print(invoice_list)
                if len(invoice_list)==1:
                    update(i,invoice_list[0])
                Promo_Date_df=Promo_df.loc[Promo_df["Invoice_Date"]==Invoice_dash_date]
                invoice_list=Promo_Date_df["Invoice_No"].unique()
                if i=='DEAL71365636 09.01.21':
                    print(Promo_df["Invoice_Date"])
                    print(invoice_list)
                if len(invoice_list)==1:
                    update(i,invoice_list[0])


            
    




