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
    Client_Code=Client_code_dic[client] # Gets the Saltix client number from the dictionary
    Retailer_Code=Retailer_Code_dic[retailer] # Gets the saltix retailer number from the dictionary
    # Inputs new query in SQL to get the client database
    cursor.execute("SELECT Salitix_client_number,Salitix_client_name,Db FROM [Salitix_Master_Data].[dbo].[salitix_client_numbers] WHERE Salitix_client_number='"+Client_Code+"';")
    User_List=cursor.fetchall() # Fetches the data from the query
    print(User_List) # Prints the data from the query
    Client_Db=User_List[0][2] # Assigns Client_Db to the database name from the query

# Connects to the client database
Client_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE='+Client_Db+';Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers') 
Client_cursor = Client_conn.cursor() # Creates a cursor object to interact with the database

# Query to get the HDR invoices from the client database (source data / ERP system)
#JR commented and replaced with line below:  HDR_Query = "SELECT Vendor_Name,Retailer_Invoice FROM ["+Client_Db+"].[dbo].[SAL_Customer_Charges_HDR_Alt] GROUP BY Vendor_Name,Retailer_Invoice"
HDR_Query = "SELECT Salitix_Customer_Number, Retailer_Invoice FROM ["+Client_Db+"].[dbo].[vw_SAL_Customer_Charges_Alt] WHERE [Salitix_Customer_Number] = '"+Retailer_Code+"' AND [CC_DTL_ID] IS NULL"
HDR_Charges_df=pd.read_sql(HDR_Query,Client_conn) # Reads the query into a pandas dataframe
HDR_list=HDR_Charges_df["Retailer_Invoice"].tolist() # Converts the dataframe into a header list

# Query to get the invoices from the scrubbed formatted data (from scrubbed invoice images)
CC_Query="SELECT Invoice_No FROM [Salitix_Scrubbed_Data_Formatted].[dbo].[Scrubbed_Customer_Charges_Ftd] WHERE Salitix_customer_number='"+Retailer_Code+"' AND Salitix_client_number ='"+Client_Code+"' GROUP BY Invoice_No"
Customer_Charges_df=pd.read_sql(CC_Query,CC_conn) # Reads the query into a pandas dataframe
CC_list=Customer_Charges_df["Invoice_No"].tolist() # Converts the dataframe into a customer charges list

# Query to get all the invoices from the scrubbed formatted data (from scrubbed invoice images)
CC_all_Query="SELECT * FROM [Salitix_Scrubbed_Data_Formatted].[dbo].[Scrubbed_Customer_Charges_Ftd] WHERE Salitix_customer_number='"+Retailer_Code+"' AND Salitix_client_number ='"+Client_Code+"'"
Customer_Charges_all_df=pd.read_sql(CC_all_Query,CC_conn) # Reads the query into a pandas dataframe

# Update function called to update the HDR invoice number in the scrubbed formatted data. Called from the for loop below
def update(HDR_No,Inv_No):
    # Inputs query in SQL to update the HDR invoice number in the scrubbed formatted data using the HDR invoice number and the invoice number
    update_Query="UPDATE [Salitix_Scrubbed_Data_Formatted].[dbo].[Scrubbed_Customer_Charges_Ftd] SET HDR_Invoice_Number = '"+HDR_No+"' WHERE Invoice_No = '"+Inv_No+"';"
    CC_cursor.execute(update_Query) # Executes the query
    CC_cursor.commit() # Commits the query

# For loop that uses the HDR list and compares each Hdr invoice number to the customer charges list
for i in HDR_list:
        print(i)
        # If the HDR invoice number is in the customer charges list it continues to the next HDR invoice number
        if i in CC_list:
            continue
        # If the retailer code is Tesco, it checks a number of different prefixes
        if Retailer_Code=="TES01":
            # Checks if the invoice image number (CC_list) matches the header number if the prefix '100' is added on to the header number (100+i)
            if "100"+i in CC_list:
                # If it is, it calls the update function with the HDR invoice number and the invoice number with the prefix '100'. Updates the HDR invoice number in the scrubbed formatted data
                update(i,"100"+i)
            # Checks if the invoice image number (CC_list) matches the header number if the prefix '1002' is added on to the header number (1002+i)
            if "1002"+i in CC_list:
                # If it is, it calls the update function with the HDR invoice number and the invoice number with the prefix '1002'. Updates the HDR invoice number in the scrubbed formatted data
                update(i,"1002"+i)
            # Checks if the invoice image number (CC_list) matches the header number if the prefix '10021' is added on to the header number (10021+i)
            if "10021"+i in CC_list:
                # If it is, it calls the update function with the HDR invoice number and the invoice number with the prefix '10021'. Updates the HDR invoice number in the scrubbed formatted data
                update(i,"10021"+i)
        # If the retailer code is Asda, it checks a number of different prefixes
        elif Retailer_Code=="ASD01":
            if i[:10] in CC_list:
                update(i,i[:10])
            if i.replace("P-","") in CC_list:
                update(i,i.replace("P-",""))
        # If the retailer code is Sainsburys, it checks a number of different prefixes
        elif Retailer_Code=="SAI01":
            # Replaces the first " _ " with "-" in the current HDR invoice number and assigns to new variable 
            i_replace_new=i.replace(" _ ","-")
            # Checks if the header number with the first " _ " replaced with "-" is in the customer charges list
            if i_replace_new in CC_list:
                # If it is, it updates the HDR invoice number in the scrubbed formatted data with the original HDR invoice number, to the customer charge it matched to
                update(i,i_replace_new)

            # Replaces the first " _ " with "_" in the current HDR invoice number and assigns to new variable
            i_replace_new1=i.replace(" _ ","_")
            # Checks if the header number with the first " _ " replaced with "_" is in the customer charges list
            if i_replace_new1 in CC_list:
                # If it is, it updates the HDR invoice number in the scrubbed formatted data with the original HDR invoice number, to the customer charge it matched to
                update(i,i_replace_new1)

            # Replaces the first "/" with "_" in the current HDR invoice number and assigns to new variable
            i_replace=i.replace("/","_")
            # Checks if the header number with the first "/" replaced with "_" is in the customer charges list
            if i_replace in CC_list:
                # If it is, it updates the HDR invoice number in the scrubbed formatted data with the original HDR invoice number, to the customer charge it matched to
                update(i,i_replace)

            # Replaces the second "/" with "_" in the current HDR invoice number replacement (line 107) and assigns to new variable
            i_replace2=i_replace.replace("/","_")
            # Checks if the header number with the second "/" replaced with "_" is in the customer charges list
            if i_replace2 in CC_list:
                # If it is, it updates the HDR invoice number in the scrubbed formatted data with the original HDR invoice number, to the customer charge it matched to
                update(i,i_replace2)

            # Replaces the second "/" with "" in the current HDR invoice number replacement (line 107) and assigns to new variable
            i_replace3=i_replace.replace("/","")
            # Checks if the header number with the second "/" replaced with "" is in the customer charges list
            if i_replace3 in CC_list:
                # If it is, it updates the HDR invoice number in the scrubbed formatted data with the original HDR invoice number, to the customer charge it matched to
                update(i,i_replace3)

            # Replaces the first "/" with " _ " in the current HDR invoice number and assigns to new variable
            i_replace4=i.replace("/"," _ ")
            # Checks if the header number with the first "/" replaced with " _ " is in the customer charges list
            if i_replace4 in CC_list:
                # If it is, it updates the HDR invoice number in the scrubbed formatted data with the original HDR invoice number, to the customer charge it matched to
                update(i,i_replace4)

            # Replaces the first "-" with "_" in the current HDR invoice number and assigns to new variable
            i_replace5=i.replace("-","_")
            # Checks if the header number with the first "-" replaced with "_" is in the customer charges list
            if i_replace5 in CC_list:
                # If it is, it updates the HDR invoice number in the scrubbed formatted data with the original HDR invoice number, to the customer charge it matched to
                update(i,i_replace5)

            # Replaces the second "-" with "_" in the current HDR invoice number replacement (line 135) and assigns to new variable
            i_replace6=i_replace5.replace("-","_")
            # Checks if the header number with the second "-" replaced with "_" is in the customer charges list
            if i_replace6 in CC_list:
                # If it is, it updates the HDR invoice number in the scrubbed formatted data with the original HDR invoice number, to the customer charge it matched to
                update(i,i_replace6)

            # Replaces the first "-" with " _ " in the current HDR invoice number and assigns to new variable
            i_replace7=i.replace("-"," _ ")
            # Checks if the header number with the first "-" replaced with " _ " is in the customer charges list
            if i_replace7 in CC_list:
                # If it is, it updates the HDR invoice number in the scrubbed formatted data with the original HDR invoice number, to the customer charge it matched to
                update(i,i_replace7)

            # Replaces the second "/" with "" in the current HDR invoice number replacement (line 135) and assigns to new variable
            i_replace8=i_replace5.replace("/","")
            # Checks if the header number with the second "/" replaced with "" is in the customer charges list
            if i_replace8 in CC_list:
                # If it is, it updates the HDR invoice number in the scrubbed formatted data with the original HDR invoice number, to the customer charge it matched to
                update(i,i_replace8)

            # If the client code is CL029 (Princes), it replaces the first "/" with "_P0175_" in the header number (client specific middle part of invoice image number)
            if Client_Code=='CL029':         
                i_replace5="RP"+i.replace("/","_P0175_")
                # Checks if the header number with the first "/" replaced with "_P0175_" is in the customer charges list
                if i_replace5 in CC_list:
                    # If it is, it updates the HDR invoice number in the scrubbed formatted data with the original HDR invoice number, to the customer charge it matched to
                    update(i,i_replace5)

            # If the client code is CL020 (Premier_Foods), it replaces the first "/" with one of two different values in the header number (client specific middle part of invoice image number)
            if Client_Code=='CL020':
                # Replaces the first "/" with "_P0819_" in the header number
                i_replace=i.replace("/","_P0819_")
                # Checks if the header number with the first "/" replaced with "_P0819_" is in the customer charges list
                if i_replace in CC_list:
                    print(i)
                    print(i_replace)
                    # If it is, it updates the HDR invoice number in the scrubbed formatted data with the original HDR invoice number, to the customer charge it matched to
                    update(i,i_replace)
                # Replaces the first "/" with "_M0587_" in the header number
                i_replace=i.replace("/","_M0587_")
                # Checks if the header number with the first "/" replaced with "_M0587_" is in the customer charges list
                if i_replace in CC_list:
                    # If it is, it updates the HDR invoice number in the scrubbed formatted data with the original HDR invoice number, to the customer charge it matched to
                    update(i,i_replace)
        # If the retailer code is Morrisons, it checks a number of different prefixes
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


                
        




