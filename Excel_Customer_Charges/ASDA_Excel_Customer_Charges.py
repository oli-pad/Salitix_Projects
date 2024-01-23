import pandas as pd
from collections import namedtuple
import os
import pyodbc

Client_code_dic={'Ab Inbev':"CL023", 'AG Barr':"CL005", 'Bacardi':"CL001",
    'Burtons':"CL003", 'Coty':"CL027",'Finsbury_Foods':"CL014",
    'Foxs':"CL999", 'Heineken':"CL028", 'Kettle Foods':"CL026", 
    'Kinnerton':"CL022", 'Maxxium':"CL012", 'Pladis':"CL002", 
    'Premier Foods':"CL020", 'Princes':"CL029", 'Tilda':"CL013", 'Youngs':"CL004",
    'Loreal':'CL030'}

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Scrubbed_Data_Staging;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

sql_command="SELECT * FROM [Salitix_Scrubbed_Data_Staging].[dbo].[Scrubbed_ASDA_Customer_Charges_Stg] WHERE Salitix_client_number='{}';"

directory_list = [ item for item in os.listdir(r"W:\Audit")]

invoice_image_folder_path="W:\Audit\{}\Invoice Images"
invoice_image_path="W:\Audit\{}\Invoice Images\ImageStagingBay\{}"

#Folders to be used for process.
audit_folder_list=[item for item in directory_list if os.path.exists(invoice_image_folder_path.format(item))]

#User input
print(audit_folder_list)
Client=str(input("Please select a client from above or type 'all'   >   "))
while Client!="all" and Client not in audit_folder_list:
    Client=str(input("Please select a client from above or type 'all'   >   "))
   
if Client=='all':
    audit_folder_list.remove('Export com')
    client_list=audit_folder_list
else:
    client_list=[Client]

#This is created by the Scrubbing process, a header level overview of the charges.
ASDA_Charges=pd.read_sql(sql_command.format(Client_code_dic[client_list[0]]),conn)

#Column names for detailed output.
Line = namedtuple('Line','Salitix_Client_Number Salitix_Customer_Number SAL_Invoice_Type Unit_Funding_Type Reference_Number Line_Description Deal_Type Invoice_No Invoice_Date Promotion_No Product_No Start_Date End_Date Quantity Unit_Price Net_Amount VAT_Rate Gross_Amount Store_Format Invoice_Description Acquisition_Ind')
lines=[]


#Path for the Excel files.
Excel_Path=r"C:\Users\python\Desktop\ASDA EXCEL FILES"

#Read through each excel and put into a dataframe
def data_extraction(Excel_Path,ASDA_Charges):
    for i in ASDA_Charges.index:
        if os.path.isfile(os.path.join(Excel_Path,str(ASDA_Charges["Invoice_No"].iloc[i])+".xlsx")):
            df = pd.read_excel(os.path.join(Excel_Path,str(ASDA_Charges["Invoice_No"].iloc[i])+".xlsx"), engine='openpyxl')
            promo(df,ASDA_Charges.iloc[i])
        else:
            non_promo(ASDA_Charges.iloc[i])
#details on a promotion.
def promo(df,info):
    product_list=df["Item Number"].drop_duplicates()
    product_list=product_list.to_list()
    product_list=[item for item in product_list if not(pd.isnull(item)) == True]
    Quantity_list=[df[df["Item Number"]==i]["Weight / Quantity"].sum() for i in product_list]
    Amount_list=[df[df["Item Number"]==i]["Accrual Amount"].sum() for i in product_list]
    Unit_Price_list=[round(Amount_list[i]/Quantity_list[i],2) for i in range(len(product_list))]
    if info["Invoice_Description"]=="Credit":
        Quantity_list=[-i for i in Quantity_list]
        Amount_list=[-i for i in Amount_list]
    for i in range(len(Quantity_list)):
        lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,info["SAL_Invoice_Type"],info["Unit_Funding_Type"],info["Reference_Number"],info["Line_Description"],info["Deal_Type"],info["Invoice_No"],info["Invoice_Date"],info["Promotion_No"],product_list[i],info["Start_Date"],info["End_Date"],Quantity_list[i],Unit_Price_list[i],Amount_list[i],info["VAT_Rate"],float(Amount_list[i])*(1+float(info["VAT_Rate"])),info["Store_Format"],info["Invoice_Description"],info["Acquisition_Ind"]))

#details on a non-promotion
def non_promo(info):
    if info["Invoice_Description"]=="Credit":
        lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,info["SAL_Invoice_Type"],info["Unit_Funding_Type"],info["Reference_Number"],info["Line_Description"],info["Deal_Type"],info["Invoice_No"],info["Invoice_Date"],info["Promotion_No"],info["Product_No"],info["Start_Date"],info["End_Date"],info["Quantity"],info["Unit_Price"],"-"+str(info["Net_Amount"]),info["VAT_Rate"],"-"+str(info["Gross_Amount"]),info["Store_Format"],info["Invoice_Description"],info["Acquisition_Ind"]))
    elif info["SAL_Invoice_Type"]=="PR":
        None
    else:
        lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,info["SAL_Invoice_Type"],info["Unit_Funding_Type"],info["Reference_Number"],info["Line_Description"],info["Deal_Type"],info["Invoice_No"],info["Invoice_Date"],info["Promotion_No"],info["Product_No"],info["Start_Date"],info["End_Date"],info["Quantity"],info["Unit_Price"],info["Net_Amount"],info["VAT_Rate"],info["Gross_Amount"],info["Store_Format"],info["Invoice_Description"],info["Acquisition_Ind"]))

def into_data_frame(lines):
    df=pd.DataFrame(lines)
    df.to_csv("oliveroakes.csv")
    #df=pd.read_csv(r"C:\Users\python\Desktop\projects\Excel_Customer_Charges\oliveroakes.csv")
    #Standardize(df,ASDA_Charges)
    insert_into_staging(df,Salitix_Client_Number,Salitix_Customer_Number)

#only returns files that exist in folder.
def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

def Standardize(df,ASDA_charges):
    invoice_list=df['Invoice_No'].unique()
    for i in invoice_list:
        invoice_total_df=df[df['Invoice_No']==i]
        invoice_total=invoice_total_df['Net_Amount'].sum()
        ASDA_Charges_invoice_df=ASDA_charges[ASDA_charges['Invoice_No']==i]
        ASDA_Charges_total=ASDA_Charges_invoice_df['Net_Invoice_Total'].sum()
        print(i)
        print(invoice_total,ASDA_Charges_total)
        print(invoice_total==ASDA_Charges_total)
        if round(float(invoice_total),2)==round(float(ASDA_Charges_total),2):
            continue
        elif float(invoice_total)==0:continue
        else:
            ratio=float(ASDA_Charges_total)/float(invoice_total)
            for j in invoice_total_df.index:
                print(j)
                #[Quantity][Net_Amount][Gross_Amount]
                Quantity=float(df.loc[j,"Quantity"])*ratio
                df.loc[j,"Quantity"]=Quantity
                Net_Amount=float(df.loc[j,"Net_Amount"])*ratio
                df.loc[j,"Net_Amount"]=Net_Amount
                Gross_Amount=float(df.loc[j,"Gross_Amount"])*ratio
                df.loc[j,"Gross_Amount"]=Gross_Amount
                df.to_csv("oliveroakes112.csv")

def insert_into_staging(df,client_code,retailer_code):
    cols = ",".join([str(i).replace(" ","_") for i in df.columns.tolist()])
    for x,row in df.iterrows():
        row_info_0=[str(j).replace("'","") for j in row]
        row_info_0[0]=client_code
        row_info_0[1]=retailer_code
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
        for x in range(len(row_info_0)):
            if row_info_0[x]=="nan":row_info_0[x]="NULL"
            elif row_info_0[x]=="None":row_info_0[x]="NULL"
            else:row_info_0[x]="'"+row_info_0[x]+"'"
        row_info=",".join([str(j) for j in row_info_0])
        sql1 = "INSERT INTO [Salitix_Scrubbed_Data_Staging].[dbo].[Scraped_ASDA_Customer_Charges_stg] (" +cols + ") VALUES ("+row_info+");"
        cursor.execute(sql1)
        cursor.commit()

Salitix_Client_Number,Salitix_Customer_Number=str(Client_code_dic[client_list[0]]),"ASD01"

data_extraction(Excel_Path,ASDA_Charges)

into_data_frame(lines)