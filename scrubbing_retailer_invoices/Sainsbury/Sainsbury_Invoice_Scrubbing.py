import os
from pathlib import Path
import re
import pdfplumber
import pandas as pd
from collections import namedtuple

#this will be the names of the columns...
Line = namedtuple('Line','Salitix_Client_Number Salitix_Customer_Number SAL_Invoice_type Unit_Funding_Type Reference_number Line_Description Deal_Type Invoice_No Invoice_Date Promotion_No Product_No Start_Date End_Date Quantity Unit_Price Net_Amount VAT_Rate Gross_Amount Store_Format Invoice_Description Acquisition_Ind')

Line2= namedtuple('Line2','Invoice_No Invoice_Total')
#This will be the Dataframe output...
lines=[]
Invoice_Totals_df=[]
check_list=[]
Invoice_Totals_dict={}
#referring for SAL codes...
SAL_CSV=pd.read_csv(r'C:\Users\Python\Desktop\projects\scrubbing_retailer_invoices\docs\Consistent Refrences for all clients\SAL_ref.csv')
description=pd.read_csv(r'C:\Users\Python\Desktop\projects\scrubbing_retailer_invoices\docs\Consistent Refrences for all clients\Line_desc_Sainsbury.csv')

def Read_pdf(file):
    pdf_text=''
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            pdf_text+=text
    return pdf_text

Invoice_Date_re=re.compile(r'Invoice(\s?)Date(\s?)[:](\s?)(\d{2})[/](\d{2})[/](\d{4})')
Invoice_No_re=re.compile(r'Invoice Number[:;] (.*)')
Reference_number=None
total_re=re.compile(r'^([0-9,]*) ([0-9,]*).(\d{2}) ([0-9,]*).(\d{2}) ([0-9,]*).(\d{2}) GBP$')
FD_Total_re=re.compile(r'^([0-9,.]*) ([0-9,.]*) ([0-9,.]*) GBP$')
#Checking the text and outputting the Invoice Info.
def Invoice_infomation(text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        Inv=Invoice_No_re.search(line)
        Inv_Date=Invoice_Date_re.search(line)
        total=total_re.search(line)
        FD_total=FD_Total_re.search(line)
        if Inv:
            Invoice_No=Inv.group(1)
            #print(Invoice_No)
        if Inv_Date:
            Invoice_Date=Inv_Date.group(4)+'/'+Inv_Date.group(5)+'/'+Inv_Date.group(6)
        if total:
            Invoice_Total=total.group(6)+'.'+total.group(7)
            Invoice_Total=Invoice_Total.replace(",","")
            Invoice_Totals_dict[Invoice_No]=Invoice_Total
        elif FD_total:
            Invoice_Total=FD_total.group(3)
            Invoice_Total=Invoice_Total.replace(",","")
            Invoice_Totals_dict[Invoice_No]=Invoice_Total
    return Invoice_No,Invoice_Date

promo_re=re.compile('Promotional(\s?)ID(\s?)[:](\s?)(\d+)')
start_re=re.compile('Billing(\s?)Start(\s?)Date(\s?)[:](\s?)(\d{2})(.*)(\d{2})(.*)(\d{4})')
end_re=re.compile('Billing(\s?)End(\s?)Date(\s?)[:](\s?)(\d{2})(.*)(\d{2})(.*)(\d{4})')
values_re=re.compile('^(\d+)/(\d+) (\d+) (.*) ([0-9,]*) ([0-9.]*) ([0-9,.]*) ([0-9,.]*) ([0-9,.]*) %$')
Core_conv_re=re.compile('^(\d+)(\s?):(.*):(.*)$')
Store_Format=None
Invoice_Description=None
Acquisition_Ind="Automatic"
def Promo_Information(text,Invoice_No,Invoice_Date):
    Invoice_Description=None
    for line in text.split('\n'):
        line = " ".join(line.split())
        promo=promo_re.search(line)
        values=values_re.search(line)
        start=start_re.search(line)
        end=end_re.search(line)
        info_desc=Core_conv_re.search(line)
        print (Invoice_No)
        # 29/05 JR added print
        if start:
            Start_Date=start.group(5)+"/"+start.group(7)+"/"+start.group(9)
        if end:
            End_Date=end.group(5)+"/"+end.group(7)+"/"+end.group(9)
        if promo:
            Promotion_No=promo.group(4)
        if info_desc:
            Invoice_Description=info_desc.group(3)+" : "+info_desc.group(4)
        if values:
            SAL_Invoice_Type='PR'
            Unit_Funding_Type='E'
            Deal_Type='Promo Retro EPOS'
            Product_No=values.group(3)
            Line_Description=values.group(4)
            Quantity=values.group(5)
            Quantity=Quantity.replace(",","")
            Unit_Price=values.group(6)
            if Unit_Price[0]=='.':
                Unit_Price="0"+Unit_Price
            Net_Amount=values.group(7)
            Net_Amount=Net_Amount.replace(",","")
            vat_amount=values.group(8)
            vat_amount=vat_amount.replace(",","")
            VAT_Rate=values.group(9)
            Gross_Amount=str(float(Net_Amount)+float(vat_amount))
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)

def FD_Information(text,Invoice_No,Invoice_Date):
    Promotion_No=None
    Product_No=None
    Start_Date=Invoice_Date
    End_Date=Invoice_Date
    group=[]
    if Invoice_No[:2]=="FD":
        for line in text.split('\n'):
            line = " ".join(line.split())
            group.append(line)
            if line == "Billing VAT VAT Total":
                SAL_Invoice_Type="FX"
                Unit_Funding_Type=""
                Deal_Type="Derogation"
                Line_Description=group[-2]
                Quantity=Invoice_Totals_dict[Invoice_No]
                Unit_Price="1"
                Net_Amount=Quantity
                Gross_Amount=Quantity
                VAT_Rate="0"
                Store_Format=None
                Invoice_Description=None
                lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
                check_list.append(Invoice_No)
                break

def into_data_frame(lines):
    df=pd.DataFrame(lines)
    df.to_csv('Oli.csv',index=False)

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

def data_extraction_Sainsburys(base_path):
    for filename in listdir_nohidden(base_path):
        try:
            #print(filename)
            text=Read_pdf(os.path.join(base_path,filename))
            Invoice_No,Invoice_Date=Invoice_infomation(text)
            Promo_Information(text,Invoice_No,Invoice_Date)
            if Invoice_No not in check_list:
                FD_Information(text,Invoice_No,Invoice_Date)
            try:invoice_integrity(Invoice_No,list(filter_list(lines,Invoice_No)))
            except:None
            if Invoice_No in check_list:
                try:
                    os.rename(os.path.join(base_path,filename),os.path.join(base_path,Invoice_No+".pdf"))
                except:
                    os.replace(os.path.join(base_path,filename),os.path.join(base_path,Invoice_No+".pdf"))
            else:continue
        except:continue
    return pd.DataFrame(lines)

def filter_list(list,inv_number):
    for a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u in list:
        if h == inv_number:
            yield h,r

def invoice_integrity(Invoice_No,list):
    total=0
    for i in list:
        total+=float(i[1])
    if abs(total-float(Invoice_Totals_dict[Invoice_No]))>5:
        check_list.remove(Invoice_No)

Salitix_Client_Number,Salitix_Customer_Number="",""

#data_extraction_Sainsburys(r"C:\Users\Python\Desktop\test\Incomplete")
#into_data_frame(lines)
