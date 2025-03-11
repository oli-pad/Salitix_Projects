import os
import pyodbc
import pandas as pd
# importing sys
from sys import argv
import sys

script,Client,Customer=argv

Client_code_dic={'Ab_Inbev':"CL023", 'AG_Barr':"CL005", 'Bacardi':"CL001",
    'Burtons':"CL003", 'Coty':"CL027",'Finsbury_Foods':"CL014",
    'Foxs':"CL999", 'Heineken':"CL028", 'Kettle Foods':"CL026", 
    'Kinnerton':"CL022", 'Maxxium':"CL012", 'Pladis':"CL002", 
    'Premier_Foods':"CL020", 'Princes':"CL029", 'Tilda':"CL013", 'Youngs':"CL004",
    'Loreal':'CL031'}

#JR renamed Premier Foods to Premier_Foods on line 14
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Scrubbed_Data_Staging;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()
cursor.execute("DELETE [Salitix_Scrubbed_Data_Staging].[dbo].[Scrubbed_Customer_Charges_Stg]")
cursor.commit()
# cursor.execute("DELETE [Salitix_Scrubbed_Data_Staging].[dbo].[Scrubbed_ASDA_Customer_Charges_Stg]")
# cursor.commit()

def insert_into_staging(df,client_code,retailer_code,asda):
    cols = ",".join([str(i).replace(" ","_") for i in df.columns.tolist()])
    for x,row in df.iterrows():
        row_info_0=[str(j).replace("'","") for j in row]
        row_info_0[0]=client_code
        row_info_0[1]=retailer_code
        row_info_0[8]=row_info_0[8][6:]+"-"+row_info_0[8][3:5]+"-"+row_info_0[8][:2]
        row_info_0[11]=row_info_0[11][6:]+"-"+row_info_0[11][3:5]+"-"+row_info_0[11][:2]
        row_info_0[12]=row_info_0[12][6:]+"-"+row_info_0[12][3:5]+"-"+row_info_0[12][:2]
        try:
            row_info_0[13]=str(round(row_info_0[13],2))
        except:None
        try:
            row_info_0[14]=str(round(row_info_0[14],2))
        except:None
        try:
             row_info_0[15]=str(round(row_info_0[15],2))
        except:None
        try:
             row_info_0[16]=str(round(row_info_0[16],2))
        except:None
        try:
             row_info_0[17]=str(round(row_info_0[17],2))
        except:None
        try:
            if float(row_info_0[16])>1:row_info_0[16]=str(float(row_info_0[16])/100)
        except:None
        for x in range(len(row_info_0)):
            if row_info_0[x]=="nan":row_info_0[x]="NULL"
            elif row_info_0[x]=="None":row_info_0[x]="NULL"
            else:row_info_0[x]="'"+row_info_0[x]+"'"
        row_info=",".join([str(j) for j in row_info_0])
        if asda=="No":
            sql1 = "INSERT INTO [Salitix_Scrubbed_Data_Staging].[dbo].[Scrubbed_Customer_Charges_Stg] (" +cols + ") VALUES ("+row_info+");"
        else:
            sql1 = "INSERT INTO [Salitix_Scrubbed_Data_Staging].[dbo].[Scrubbed_ASDA_Customer_Charges_Stg] (" +cols + ") VALUES ("+row_info+");"
        cursor.execute(sql1)
        cursor.commit()


#List of things in the Audit folder.
directory_list = [ item for item in os.listdir(r"W:\Audit")]

invoice_image_folder_path="W:\Audit\{}\Invoice Images"
invoice_image_path="W:\Audit\{}\Invoice Images\ImageStagingBay\{}"

#Folders to be used for process.
audit_folder_list=[item for item in directory_list if os.path.exists(invoice_image_folder_path.format(item))]

if Client=='manual':
    #User input
    print(audit_folder_list)
    Client=str(input("Please select a client from above or type 'all'   >   "))
    while Client!="all" and Client not in audit_folder_list:
        Client=str(input("Please select a client from above or type 'all'   >   "))
   
if Client=='all':
    audit_folder_list.remove('Export com')
    client_list=audit_folder_list
    print(Client)
    print("ALL")
else:
    client_list=[Client]
    print(client_list)

for client in client_list:
    if "Tesco" in Customer:
        Tesco_image_folder=invoice_image_path.format(client,"Tesco")
        print(Tesco_image_folder)
        print(Client_code_dic[client])
        # adding Folder_2/subfolder to the system path
        sys.path.insert(0, r'C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\Tesco')
    
        # importing the hello
        from Tesco_Invoice_Scrubbing import data_extraction_Tesco
        Tesco_df=data_extraction_Tesco(Tesco_image_folder)
        insert_into_staging(Tesco_df,Client_code_dic[client],"TES01","No")

    if "Morrisons" in Customer:
        morrisons_image_folder=invoice_image_path.format(client,"Morrisons")
        print(morrisons_image_folder)
        print(Client_code_dic[client])
        # adding Folder_2/subfolder to the system path
        sys.path.insert(0, r'C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\Morrisons')
    
        # importing the hello
        from Morrisons_Invoice_Scrubbing import data_extraction_morrisons
        morrisons_df=data_extraction_morrisons(morrisons_image_folder)
        insert_into_staging(morrisons_df,Client_code_dic[client],"MOR01","No")
#29/05 JR changed Sainsburys to Sainsbury (that's the name on the flask)
    if "Sainsbury" in Customer:
        sainsbury_image_folder=invoice_image_path.format(client,"Sainsburys")
        print(sainsbury_image_folder)
        print(Client_code_dic[client])
        # adding Folder_2/subfolder to the system path
        sys.path.insert(0, r'C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\Sainsbury')
    
        # importing the hello
        from Sainsbury_Invoice_Scrubbing import data_extraction_Sainsburys
        sainsbury_df=data_extraction_Sainsburys(sainsbury_image_folder)
        insert_into_staging(sainsbury_df,Client_code_dic[client],"SAI01","No")

    if "ASDA" in Customer:
        asda_image_folder=invoice_image_path.format(client,"ASDA")
        print(asda_image_folder)
        print(Client_code_dic[client])
        # adding Folder_2/subfolder to the system path
        sys.path.insert(0, r'C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\ASDA')
    
        # importing the hello
        from ASDA_Invoice_Scrubbing import data_extraction_ASDA
        ASDA_df=data_extraction_ASDA(asda_image_folder)
        insert_into_staging(ASDA_df,Client_code_dic[client],"ASD01","Yes")



