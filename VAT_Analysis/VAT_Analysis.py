from collections import namedtuple
import pyodbc
import pandas as pd
from datetime import datetime
import numpy as np
import openpyxl
from openpyxl import load_workbook
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import os

VAT_df=pd.DataFrame(columns=["Product_No","VAT_Rate"])
#Connection for Customer Charges will change, currently using scrubbed files
#In Edringtons case they are in the Db so will use these as a test.
CC_df=pd.read_csv(r"C:\Users\Python\Desktop\VAT\Customer_Charges\Pladis_Tesco_Correction_09.08.2022.csv")

Exc_df=pd.DataFrame(columns=list(CC_df.columns.values))

#master_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
#master_cursor = master_conn.cursor()
#For User Input.
#Client_Code=input("What's the Client Code?  >")
#Retailer_Code=input("What's the Retailer Code?  >")
#Date_period_1=input("Start date?  >")
#Date_period_2=input("End date?  >")
#To store the name of the databse for the relevant client.
#master_cursor.execute("SELECT Salitix_client_number,Salitix_client_name,Db FROM [Salitix_Master_Data].[dbo].[salitix_client_numbers] WHERE Salitix_client_number='"+Client_Code+"';")
#User_List=master_cursor.fetchall()
#Client_Db=User_List[0][2]
#Create the Vat prod file with CC
def VAT_file(CC_df):
    Product_numbers=CC_df.Product_No.unique()
    for i in Product_numbers:
        CC_prod_df=CC_df[CC_df["Product_No"]==i]
        VAT_Rates=CC_prod_df.VAT_Rate.unique()
        VAT_df.loc[len(VAT_df.index)] =[i,min(VAT_Rates)]
    VAT_df.to_csv("VAT_prod_file.csv",index=False)

def VAT_analysis(CC_df,PF):
    for i in CC_df.index:
        row=CC_df.iloc[i]
        ind=PF.index[PF["Product_No"]==row["Product_No"].iloc[0]]
        if row["VAT_Rate"].iloc[0]==PF["VAT_Rate"].iloc[ind[0]] :
            continue
        else:
            Exc_df.loc[len(VAT_df.index)]=row.iloc[i]
    Exc_df.to_csv("Exceptions.csv",index=False)

VAT_file(CC_df)
VAT_analysis(CC_df,VAT_df)
