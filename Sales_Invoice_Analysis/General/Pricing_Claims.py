import pyodbc
import pandas as pd
import os
import sys

script, retailer_folder,client_folder = sys.argv

# Connect to SQL Server
Exceptions_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Claims_Database;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = Exceptions_conn.cursor()

ACR_Ftd = "SELECT * FROM [Salitix_Claims_Database].[dbo].[ACR_Automated_Claim_Report_Ftd] WHERE Claim_Category = 'Cost Price Discrepancy';"
ACR_Ftd_df=pd.read_sql(ACR_Ftd,Exceptions_conn)

dict={"Ab_Inbev":"CL023","AG Barr":"CL005","Bacardi":"CL001"
      ,"Burtons":"CL003","Coty":"CL027","Finsbury Foods":"CL014"
      ,"Heineken":"CL028","Kettle Foods":"CL026","Loreal":"CL031"
      ,"Maxxium":"CL012","Pladis":"CL002","Premier_Foods":"CL020"
      ,"Princes":"CL029","Tilda":"CL013"}

retailer_dict = {
    "Morrisons": "MOR01",
    "Tesco": "TES01",
    "Sainsbury": "SAI01",
    "Asda": "ASD01",
    "COOP": "COO01",
    "Waitrose": "WAI01",
    "Aldi": "ALD01",
    "Lidl": "LID01",
    "Boots": "BOO01",
    "Superdrug": "SUP01",
    "Amazon": "AMA01",
    "Ocado": "OCA01",
    "Iceland": "ICE01",
}

print(dict)
print("If the client code is not in the dictionary, please add it to the dictionary and re-run the script.")
# print("C:\Users\python\Desktop\projects\Sales_Invoice_Analysis\General\Pricing_Claims.py, Line 15~, variable dict")

def get_potential_claims(dir):
    files=[]
    for file in os.listdir(dir):
        if file.endswith(".xlsx"):
            files.append(os.path.join(dir,file))
    return files

def get_claim_info(file):
    df=pd.read_excel(file)
    Claim_Total=round(df["Claim"].sum(),2)
    start_date=df["pricing_date"].min()
    end_date=df["pricing_date"].max()
    return Claim_Total,start_date,end_date

def report_line(file,filename):
    filename_detail=filename.split(" ")
    print(filename)
    Claim_Total,start_date,end_date=get_claim_info(file)
    return["'Not Reviewed'","'Pricing'","''","'"+filename_detail[0]+"'","'"+str(Claim_Total)+"'","'"+str(start_date)+"'","'"+str(end_date)+"'","'"+str(start_date)+"'","'"+str(end_date)+"'"
     ,"'"+str(start_date)+"'","'"+str(end_date)+"'","'"+str(file)+"'","'NULL'","NULL"]

def insert_into_table(list):
    if list==[None]:return
    cols="Reviewed_Status,Claim_Category,Period,Product_No,Potential_Value,EPOS_Start_Date,EPOS_End_Date,Promo_Start_Date,Promo_End_Date,SI_Start_Date,SI_End_Date,Evidence_File_Path,Promo_Schedule_Promo_ID,Invoice_List,Client_Code,Customer_Code,Audit_Year"
    for i in list:
        file_list=i[-3].split("\\")
        Client_Code=dict[file_list[5]]
        Retailer_Code=retailer_dict[retailer_folder]
        row_info=",".join([str(j) for j in i])
        Audit_Year=i[5]
        Audit_Year=Audit_Year.split("-")[0]+"'"
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

file_list=get_potential_claims(r"W:\Admin\Claims Db\Pricing Claims\{}\{}".format(retailer_folder,client_folder))
df=[]
for file in file_list:
    df.append(report_line(file,os.path.basename(file)))
insert_into_table(df)