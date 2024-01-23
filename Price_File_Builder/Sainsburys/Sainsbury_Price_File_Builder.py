import os
from pathlib import Path
import re
import pdfplumber
import pandas as pd
from collections import namedtuple
import numpy as np
from sys import argv
import pyodbc

Line=namedtuple('Line','Salitix_client_number Salitix_customer_number Product_No Effective_Date Std_case_size Current_cost Std_case_cost VAT SourceFile SourceInd')
lines=[]
SourceInd="R"
script,cpc_from_path,nlf_from_path,Salitix_client_number,Salitix_client_name=argv

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Pricing_Data_Staging;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()
conn2 = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALSQL02;DATABASE=Salitix_Pricing_Data_Formatted;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor2 = conn2.cursor()

#CPC Regular Expression compile
effective_date_re=re.compile(r'Effective Date (\d{2})[/](\d{2})[/](\d{4})')
line_detail_re=re.compile(r'(\d+)[/](\d+) (\d+) (.*) (\d+) GBP Case (.*)[.](\d+) (.*)[.](\d+)')
line_detail_re_2=re.compile(r'^(\d+) (.*) (\d+) GBP Case (.*)[.](\d+) (.*)[.](\d+)$')
line_detail_re_Unit=re.compile(r'(\d+)[/](\d+) (\d+) (.*) (\d+) GBP Unit (.*)[.](\d+) (.*)[.](\d+)')
line_detail_re_Unit_2=re.compile(r'^(\d+) (.*) (\d+) GBP Unit (.*)[.](\d+) (.*)[.](\d+)$')
#NLF Regular Expression compile
date_re=re.compile(r'Target on sale effective date (\d{2})[/](\d{2})[/](\d{4})')
VAT_20_re=re.compile(r'VAT Code 20.0 Standard')
VAT_17_re=re.compile(r'VAT Code 17.5 Standard')
VAT_15_re=re.compile(r'VAT Code (.*) Partial')
VAT_0_re_1=re.compile(r'VAT Code Non')
VAT_0_re_2=re.compile(r'VAT Code 0.00')
case_size_re=re.compile(r'Case Size (\d+) ')
case_cost_re=re.compile(r'SKU Case Cost (.*)[.](.*) Layers')
prod_number_re=re.compile(r'SKU Number (\d+) ')
no_SKU_re=re.compile(r'SKU Number')
category_re=re.compile(r'Category (.*) Buyer')

def sainos_cpc_extract(file,SourceFile):
    VAT=0
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            if text==None:continue
            for line in text.split('\n'):
                line=" ".join(line.split())
                effective=effective_date_re.search(line)
                line_detail=line_detail_re.search(line)
                line_detail_2=line_detail_re_2.search(line)
                line_detail_unit=line_detail_re_Unit.search(line)
                line_detail_unit_2=line_detail_re_Unit_2.search(line)
                category=category_re.search(line)
                if effective:
                    #Effective_Date=effective.group(1)+"/"+effective.group(2)+"/"+effective.group(3)
                    Effective_Date="'"+effective.group(3)+"-"+effective.group(2)+"-"+effective.group(1)+"'"
                elif line_detail:
                    Product_No=line_detail.group(3)
                    Std_case_size=line_detail.group(5)
                    Std_case_cost=line_detail.group(8)+"."+line_detail.group(9)
                    Current_cost=line_detail.group(6)+"."+line_detail.group(7)
                    if VAT==None:VAT=0
                    lines.append(Line("'"+Salitix_client_number+"'","'"+Salitix_customer_number+"'",Product_No,Effective_Date,Std_case_size,Current_cost,Std_case_cost,VAT,"'"+SourceFile+"'","'"+SourceInd+"'"))
                elif line_detail_2 and not line_detail:
                    Product_No=line_detail_2.group(1)
                    Std_case_size=line_detail_2.group(3)
                    Std_case_cost=line_detail_2.group(6)+"."+line_detail_2.group(7)
                    Current_cost=line_detail_2.group(4)+"."+line_detail_2.group(5)
                    if VAT==None:VAT=0
                    lines.append(Line("'"+Salitix_client_number+"'","'"+Salitix_customer_number+"'",Product_No,Effective_Date,Std_case_size,Current_cost,Std_case_cost,VAT,"'"+SourceFile+"'","'"+SourceInd+"'"))
                elif line_detail_unit:
                    Product_No=line_detail_unit.group(3)
                    Std_case_size=line_detail_unit.group(5)
                    Std_case_cost=line_detail_unit.group(8)+"."+line_detail_unit.group(9)
                    Std_case_cost=float(Std_case_cost)*float(Std_case_size)
                    Std_case_cost=str(Std_case_cost)
                    Current_cost=line_detail_unit.group(6)+"."+line_detail_unit.group(7)
                    Current_cost=float(Current_cost)*float(Std_case_size)
                    Current_cost=str(Current_cost)
                    if VAT==None:VAT=0
                    lines.append(Line("'"+Salitix_client_number+"'","'"+Salitix_customer_number+"'",Product_No,Effective_Date,Std_case_size,Current_cost,Std_case_cost,VAT,"'"+SourceFile+"'","'"+SourceInd+"'"))
                elif line_detail_unit_2 and not line_detail_unit:
                    Product_No=line_detail_unit_2.group(1)
                    Std_case_size=line_detail_unit_2.group(3)
                    Std_case_cost=line_detail_unit_2.group(6)+"."+line_detail_unit_2.group(7)
                    Std_case_cost=float(Std_case_cost)*float(Std_case_size)
                    Std_case_cost=str(Std_case_cost)
                    Current_cost=line_detail_unit_2.group(4)+"."+line_detail_unit_2.group(5)
                    Current_cost=float(Current_cost)*float(Std_case_size)
                    Current_cost=str(Current_cost)
                    if VAT==None:VAT=0
                    lines.append(Line("'"+Salitix_client_number+"'","'"+Salitix_customer_number+"'",Product_No,Effective_Date,Std_case_size,Current_cost,Std_case_cost,VAT,"'"+SourceFile+"'","'"+SourceInd+"'"))
                elif category:
                    if category.group(1)=="BWS":
                        VAT=20
                    elif category.group(1)=="Impulse Food" or category.group(1)=="Canned & Packaged" or category.group(1)=="Meal Solutions" or category.group(1)=="Meat, Fish & Poultry":
                        VAT=0
                    elif "Counters" in category.group(1) or "Bakery" in category.group(1) or "Value" in category.group(1) or "Frozen" in category.group(1):
                        VAT=0
                    else:
                        print("category error")
                        print(category.group(1))
                        break

def sainos_nlf_extract(file,SourceFile):
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            if text==None:continue
            for line in text.split('\n'):
                line=" ".join(line.split())
                date=date_re.search(line)
                VAT20=VAT_20_re.search(line)
                VAT17=VAT_17_re.search(line)
                VAT15=VAT_15_re.search(line)
                VAT0=VAT_0_re_1.search(line)
                VAT0_2=VAT_0_re_2.search(line)
                case_size=case_size_re.search(line)
                case_cost=case_cost_re.search(line)
                prod_number=prod_number_re.search(line)
                no_SKU=no_SKU_re.search(line)
                if VAT20:
                    VAT=20
                elif VAT17:
                    VAT=17.5
                elif VAT15:
                    VAT=VAT15.group(1)
                elif VAT0:
                    VAT=0
                elif VAT0_2:
                    VAT=0
                elif case_size:
                    Std_case_size=case_size.group(1)
                elif case_cost:
                    Current_cost="NULL"
                    Std_case_cost=case_cost.group(1)+"."+case_cost.group(2)
                    Std_case_cost=Std_case_cost.replace(",","")
                elif prod_number:
                    Product_No=prod_number.group(1)
                elif no_SKU:
                    Product_No="NULL"
                elif date:
                    #Effective_Date=date.group(1)+"/"+date.group(2)+"/"+date.group(3)
                    Effective_Date="'"+date.group(3)+"-"+date.group(2)+"-"+date.group(1)+"'"
                    if VAT==None:VAT=0
                    lines.append(Line("'"+Salitix_client_number+"'","'"+Salitix_customer_number+"'",Product_No,Effective_Date,Std_case_size,Current_cost,Std_case_cost,VAT,"'"+SourceFile+"'","'"+SourceInd+"'"))

def data_extraction(path1,path2):
    for filename in listdir_nohidden(path1):
        print(filename)
        if ".pdf" not in filename:continue
        sainos_cpc_extract(os.path.join(path1,filename),filename)
    for filename in listdir_nohidden(path2):
        print(filename)
        if ".pdf" not in filename:continue
        sainos_nlf_extract(os.path.join(path2,filename),filename)

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

def into_data_frame(lines):
    df=pd.DataFrame(lines)
    df.to_csv('Z:\Pricing\\'+Salitix_customer_name+'_PRICE_FILE_'+Salitix_client_name+'.csv',index=True)
    cols = ",".join([str(i) for i in df.columns.tolist()])
    for x,row in df.iterrows():
        row_info=",".join([str(j) for j in row])
        sql = "INSERT INTO [Salitix_Pricing_Data_Staging].[dbo].[Pricing_Sainsburys_Stg] (" +cols + ") VALUES ("+row_info+");"
        cursor.execute(sql)
        cursor.commit()
    conn.close()
    cursor2.execute("EXEC [Salitix_Pricing_Data_Formatted].[dbo].[prc_Pricing_Sainsburys_Ftd_Insert] 'SAINSBURY_PRICE_FILE_"+Salitix_client_name+".csv'")
    cursor2.commit()
    conn2.close()


Salitix_customer_name="SAINSBURY"
Salitix_customer_number="SAI01"

data_extraction(cpc_from_path,nlf_from_path)
into_data_frame(lines)
