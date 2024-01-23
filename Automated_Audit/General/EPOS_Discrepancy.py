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
from collections import Counter

def get_EPOS_df(promotion,Client_Code,Retailer_Code):
    #connecting to the EPOS in SQL server.
    EPOS_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_EPOS_Data_Formatted;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
    EPOS_cursor = EPOS_conn.cursor()
    EPOS_query="SELECT * FROM [Salitix_EPOS_Data_Formatted].[dbo].[Salitix_EPOS_ftd] WHERE salitix_client_number='" \
        + Client_Code + "' AND salitix_customer_number='" + Retailer_Code + "' AND Retailer_Product_Number='{}' AND Calendar_Date BETWEEN '{}' AND '{}';"
    Full_Exceptions_Report=[]
    EPOS_df=pd.DataFrame()
    for i in promotion:
        EPOS_df=EPOS_df._append(pd.read_sql(EPOS_query.format(i[16],i[11],i[12]),EPOS_conn))
    return EPOS_df

def get_CC_df(promotion,Customer_Charges_df):
    CC_df = pd.DataFrame()
    for i in promotion:
        CC_df = CC_df._append(Matching_CC(i,Customer_Charges_df))
    return CC_df

def Matching_CC(row,Customer_Charges_df):
    Product_CC_df=Customer_Charges_df[Customer_Charges_df["Product_No"]==float(row[16])]
    if Product_CC_df.empty==True:
        Product_CC_df=Customer_Charges_df[Customer_Charges_df["Product_No"]==row[16]]
    if Product_CC_df.empty==True:
        Product_CC_df=Customer_Charges_df[Customer_Charges_df["Product_No"]=="0"+str(row[16])]
    if Product_CC_df.empty==True:
        Product_CC_df=Customer_Charges_df[Customer_Charges_df["Product_No"]==str(row[16]).replace("0","")]  

    Date_CC_df=Product_CC_df[Product_CC_df["End_Date"]>=row[11]]
    Date_CC_df=Date_CC_df[Date_CC_df["Start_Date"]<=row[12]]
    if Date_CC_df.empty==True:
        return Date_CC_df #,Invoice_list(Date_CC_df)
    Promo_Counts = Counter(Date_CC_df["Promotion_No"].tolist())
    Promo_Number = Promo_Counts.most_common(1)
    if len(Promo_Number)>1:
    
        comb_df=Date_CC_df[Date_CC_df["Promotion_No"]==Promo_Number[0][0]]
        for i in range(len(Promo_Number)):
            if i==0:continue
            comb_df=comb_df.append(Date_CC_df[Date_CC_df["Promotion_No"]==Promo_Number[0][i]])
        return comb_df
    else:
        Date_CC_df=Date_CC_df[Date_CC_df["Promotion_No"]==Promo_Number[0][0]]
        #Less than or equal to the dates on the customer charges
        return Date_CC_df  # ,Invoice_list(Date_CC_df)

def Invoice_list(df):
    invoices=df["Invoice_No"].unique()
    string_list="'"
    invoices=sorted(invoices)
    for i in invoices:
       
        string_list+=str(i)+','
    string_list=replace_last(string_list,",","")
    string_list+="'"
    return string_list

def Product_list(df):
    products=df["Retailer_Product_Number"].unique()
    string_list="'"
    products=sorted(products)
    for i in products:
       
        string_list+=str(i)+','
    string_list=replace_last(string_list,",","")
    string_list+="'"
    return string_list

def Promo_Number_List(df):
    promos=df["Retailer_promotion_number"].unique()
    string_list="'"
    promos=sorted(promos)
    for i in promos:
       
        string_list+=str(i)+','
    string_list=replace_last(string_list,",","")
    string_list+="'"
    return string_list

def replace_last(string, find, replace):
    reversed = string[::-1]
    replaced = reversed.replace(find[::-1], replace[::-1], 1)
    return replaced[::-1]

def participation(Standard_RSP,Promo_RSP,Qty_Sold,Sales_Value):
    if Qty_Sold==0 or Sales_Value==0:
        return 1,0
    SV_Std_price=float(Standard_RSP)*float(Qty_Sold)
    SV_Pro_price=float(Promo_RSP)*float(Qty_Sold)
    Average_RSP=float(Sales_Value)/float(Qty_Sold)
    Full_Giveaway=SV_Std_price-SV_Pro_price
    Act_Giveaway=SV_Std_price-Sales_Value
    Promotional_partcipation=Act_Giveaway/Full_Giveaway
    if Promotional_partcipation>1:
        Promotional_partcipation=1
    elif Promotional_partcipation<0:
        Promotional_partcipation=0
    Promotional_Units=Promotional_partcipation*Qty_Sold
    return Promotional_partcipation,Promotional_Units

def compare_EPOS_CC(EPOS_df,CC_df,PS_df):
    Product_list=EPOS_df["Retailer_Product_Number"].unique().tolist()
    EPOS_Product_sums = [EPOS_df[EPOS_df["Retailer_Product_Number"]==i]["Salitix_EPOS_Qty"].sum() for i in Product_list]
    EPOS_Product_Values = [EPOS_df[EPOS_df["Retailer_Product_Number"]==i]["Salitix_EPOS_Value"].sum() for i in Product_list]
    CC_Product_sums = [CC_df[CC_df["Product_No"]==i]["Quantity"].sum() for i in Product_list]
    CC_Product_Unit_Funding = [CC_df[CC_df["Product_No"]==i]["Unit_Price"].mean() for i in Product_list]
    Std_Price = [PS_df[PS_df["Retailer_Product_Number"]==i]["Standard_Selling_Price"].mean() for i in Product_list]
    Promo_Price = [PS_df[PS_df["Retailer_Product_Number"]==i]["Promotional_Selling_Price"].mean() for i in Product_list]
    Promotional_partcipation=[]
    Promotional_Units=[]
    for i in range(len(Product_list)):
        Promotional_partcipation.append(participation(Std_Price[i],Promo_Price[i],EPOS_Product_sums[i],EPOS_Product_Values[i])[0])
        Promotional_Units.append(participation(Std_Price[i],Promo_Price[i],EPOS_Product_sums[i],EPOS_Product_Values[i])[1])
    EPOS_Product_sums = [round(i,2) for i in EPOS_Product_sums]
    CC_Product_sums = [round(i,2) for i in CC_Product_sums]
    EPOS_CC_df=pd.DataFrame()
    EPOS_CC_df["Product_No"]=Product_list
    EPOS_CC_df["EPOS_Quantity"]=EPOS_Product_sums
    EPOS_CC_df["EPOS_Value"]=EPOS_Product_Values
    EPOS_CC_df["CC_Quantity"]=CC_Product_sums
    EPOS_CC_df["CC_Unit_Funding"]=CC_Product_Unit_Funding
    EPOS_CC_df["Standard_Selling_Price"]=Std_Price
    EPOS_CC_df["Promotional_Selling_Price"]=Promo_Price
    EPOS_CC_df["Promotional_partcipation"]=Promotional_partcipation
    EPOS_CC_df["Promotional_Units"]=Promotional_Units
    EPOS_CC_df["Difference"]=EPOS_CC_df["CC_Quantity"]-EPOS_CC_df["Promotional_Units"]
    EPOS_CC_df["Difference_Unit_Funding"]=EPOS_CC_df["Difference"]*EPOS_CC_df["CC_Unit_Funding"]
    return float(EPOS_CC_df["Promotional_partcipation"].mean()),float(EPOS_CC_df["Difference_Unit_Funding"].sum())

def EPOS_Discrepency(Client_Code,Retailer_Code,PS_df,CC_df):
    Exceptions_Report=[]
    
    #getting the list of years and months.
    years=PS_df["Audit_Year"].unique().tolist()
    months=PS_df["Promo_period"].unique().tolist()
    
    #get the list of promotions per year and month.
    promotions={}
    for i in years:
        for j in months:
            promotions[str(i)+' '+str(j)] = PS_df[(PS_df["Audit_Year"]==i)&(PS_df["Promo_period"]==j)]['ID'].tolist()

    for i in promotions:
        #function to get a df of the epos for a promotion.
        EPOS_df=get_EPOS_df(PS_df[PS_df['ID'].isin(promotions[i])].values.tolist(),Client_Code,Retailer_Code)

        if EPOS_df.empty==True:
            continue

        #function to get a df of the customer charges for a promotion.
        CC_df=get_CC_df(PS_df[PS_df['ID'].isin(promotions[i])].values.tolist(),CC_df)

        #function to compare the two df's
        avg_participation,total_value = compare_EPOS_CC(EPOS_df,CC_df,PS_df[PS_df['ID'].isin(promotions[i])])

        Instore_Start_Date = PS_df[PS_df['ID'].isin(promotions[i])]["Instore_Start_Date"].tolist()[0]
        Instore_End_Date = PS_df[PS_df['ID'].isin(promotions[i])]["Instore_End_Date"].tolist()[0]

        if total_value > 1000:
            if avg_participation <= 0.9:
                Exceptions_Report.append(
                    ["'Not Reviewed'","'EPOS Discrepancy'","'"+str(i).replace("'","")+"'",Product_list(PS_df[PS_df['ID'].isin(promotions[i])]),
                    "'"+str(total_value)+"'","'"+str(Instore_Start_Date)+"'","'"+str(Instore_End_Date)+"'",
                    "'"+str(Instore_Start_Date)+"'","'"+str(Instore_End_Date)+"'","'"+str(Instore_Start_Date)+"'","'"+str(Instore_End_Date)+"'",
                    "NULL",Promo_Number_List(PS_df[PS_df['ID'].isin(promotions[i])]),Invoice_list(CC_df)]
                    )
    print(Exceptions_Report)
    return Exceptions_Report


    

        
