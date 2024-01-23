import os
from pathlib import Path
#Below for regular expression analysis
import re
#Below is what reads the pdf page by page and stores it as a variable
import pdfplumber
import pandas as pd
from collections import namedtuple

#This will be the names of the columns that from the DataFrame.
Line = namedtuple('Line','Salitix_Client_Number Salitix_Customer_Number SAL_Invoice_Type Unit_Funding_Type Reference_Number Line_Description Deal_Type Invoice_No Invoice_Date Promotion_No Product_No Start_Date End_Date Quantity Unit_Price Net_Amount VAT_Rate Gross_Amount Store_Format Invoice_Description Acquisition_Ind Net_Invoice_Total')
#Dictionary below to assign the invoice total to the invoice.
Line2= namedtuple('Line2','Invoice_No Invoice_Total')
#THis will be the Dataframe output...
lines=[]
Invoice_Totals_df=[]
check_list=[]
Invoice_Totals_dict={}

Reference_Number=""
Line_Description=""
'''Change below as directories change'''
#This is to reference deal types and the codes associated with these.
DEAL_CSV=pd.read_csv(r'C:\Users\Python\Desktop\projects\scrubbing_retailer_invoices\docs\Deal_Type_Check.csv')
'''DO NOT CHANGE BELOW FROM HERE'''
#Read_pdf function Stores the pdf as a list of text.
def Read_pdf(file):
    pdf_text=''
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            pdf_text+=text
    return pdf_text

#Function to determine if the Invoice is a credit or debit.
def Debit_or_credit(text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        if "CREDIT NOTE" in line:
            return False
        elif "INVOICE" in line:
            return True

#RegEx for the Deal type on the pdf.
SAL_re=re.compile(r'^Agreement Type (.*)$')
SAL_Deal_re=re.compile(r'DEAL TYPE (.*)')
#Checking the text and outputting the deal types.
def Deal_Type_Check(file,text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        SAL=SAL_re.search(line)
        SAL_1=SAL_Deal_re.search(line)
        if SAL:
            Deal_Type=SAL.group(1)
            Start=DEAL_CSV.loc[DEAL_CSV['Deal_type']==Deal_Type]
            SAL_ref=Start['INV_ref'].iloc[0]
            Unit_ref=Start['Unit_ref'].iloc[0]
            return SAL_ref,Unit_ref,Deal_Type
        if SAL_1:
            Deal_Type=SAL_1.group(1)
            #print(Deal_Type)
            Start=DEAL_CSV.loc[DEAL_CSV['Deal_type']==Deal_Type]
            SAL_ref=Start['INV_ref'].iloc[0]
            Unit_ref=Start['Unit_ref'].iloc[0]
            return SAL_ref,Unit_ref,Deal_Type
    SAL_ref,Unit_ref,Deal_Type="MS",None,""
    return SAL_ref,Unit_ref,Deal_Type

#Regex for invoice infomation
Invoice_No_re=re.compile(r'Invoice(.*)Number: (\d+)')
Invoice_Date_re=re.compile(r'Invoice(.*)Date(.*):?(.*)(\d{2})/(\d{2})/(\d{4})')
total_re=re.compile(r'VAT(.*)Exclusive(.*)Amount ([0-9,.]*)')

credit_re=re.compile(r'Credit Number: (\d+)$')
credit_Date_re=re.compile(r'Credit(.*)Date(.*): (\d{2})/(\d{2})/(\d{4})')
#Checking the text and outputting the Invoice Info.
def Invoice_infomation(text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        Inv=Invoice_No_re.search(line)
        Inv_Date=Invoice_Date_re.search(line)
        total=total_re.search(line)
        credit=credit_re.search(line)
        credit_date=credit_Date_re.search(line)
        if Inv:
            Invoice_No=Inv.group(2)
            Invoice_No=Invoice_No.replace(" ","")
        if credit:
            Invoice_No=credit.group(1)
            Invoice_No=Invoice_No.replace(" ","")
        if Inv_Date:
            Invoice_Date=Inv_Date.group(4)+'/'+Inv_Date.group(5)+'/'+Inv_Date.group(6)
        if credit_date:
            Invoice_Date=credit_date.group(3)+'/'+credit_date.group(4)+'/'+credit_date.group(5)
        if total:
            Invoice_Total=total.group(3)
            Invoice_Total=Invoice_Total.replace(",","")
    Invoice_Totals_df.append(Line2(Invoice_No,Invoice_Total))
    Invoice_Totals_dict[Invoice_No]=Invoice_Total
    return Invoice_No,Invoice_Date,Reference_Number

#Regex for Retro Epos Promotions.
Promo_re_1=re.compile(r'Agreement (\d+)')
#Regex for date
date_re_1=re.compile(r'^Billing Period (\d{2})/(\d{2})/(\d{4}) To (\d{2})/(\d{2})/(\d{4})')
VAT_Rate_Re=re.compile(r'VAT Rate ([0-9.]*)(\s?)%')
#Checking the text and outputting the line level promo info.
def Promo_Information(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number):
    for line in text.split('\n'):
        line = " ".join(line.split())
        promo=Promo_re_1.search(line)
        date=date_re_1.search(line)
        vat=VAT_Rate_Re.search(line)
        if promo:
            Promotion_No=promo.group(1)
        if date:
            Start_Date=date.group(1)+"/"+date.group(2)+"/"+date.group(3)
            End_Date=date.group(4)+"/"+date.group(5)+"/"+date.group(6)
        if vat:
            Store_Format,Invoice_Description,Acquisition_Ind=None,None,'Automatic'
            VAT_Rate=vat.group(1)
            if "20" in VAT_Rate:
                VAT_Rate=0.2
            else:
                VAT_Rate=0
            Product_No,Quantity,Unit_Price,Net_Amount,Gross_Amount=None,None,None,None,None
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind,Invoice_Totals_dict[Invoice_No]))
            check_list.append(Invoice_No)
            Product_No=None
            date=None

#Regex for Retro Epos Promotions.
Promo_re=re.compile(r'Agreement Number (\d+)')
#Regex for date
date_re=re.compile(r'Agreement Validity (\d{2})/(\d{2})/(\d{4}) To (\d{2})/(\d{2})/(\d{4})')
def Credit_Information(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number):
    for line in text.split('\n'):
        line = " ".join(line.split())
        promo=Promo_re.search(line)
        date=date_re.search(line)
        vat=VAT_Rate_Re.search(line)
        #print(line)
        ###blanks here to get from retail link###
        if promo:
            Promotion_No=promo.group(1)
        if date:
            Start_Date=date.group(1)+"/"+date.group(2)+"/"+date.group(3)
            End_Date=date.group(4)+"/"+date.group(5)+"/"+date.group(6)
        if vat:
            Store_Format,Invoice_Description,Acquisition_Ind=None,None,'Automatic'
            VAT_Rate=vat.group(1)
            if "20" in VAT_Rate:
                VAT_Rate=0.2
            else:
                VAT_Rate=0
            Product_No,Quantity,Unit_Price,Net_Amount,Gross_Amount=None,None,None,None,None
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind,Invoice_Totals_dict[Invoice_No]))
            check_list.append(Invoice_No)
            Product_No=None
            date=None

Invoice_credited_re=re.compile(r"[iI]nvoice (\d+)")
Case_move_re=re.compile(r"CASE MOVEMENT")
Deal_credited_re=re.compile(r"[Dd]eal (\d+)")
def Credit_Misc_Information(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number):
    for line in text.split('\n'):
        line = " ".join(line.split())
        ###blanks here to get from retail link###
        Invoice_credited=Invoice_credited_re.search(line)
        Case_move=Case_move_re.search(line)
        Deal_credited=Deal_credited_re.search(line)
        vat=VAT_Rate_Re.search(line)
        if vat:
            Net_Amount=Invoice_Totals_dict[Invoice_No]
            VAT_Rate=vat.group(1)
            if "20" in VAT_Rate:
                VAT_Rate=0.2
            else:
                VAT_Rate=0
            Gross_Amount=float(Net_Amount)*(1+VAT_Rate)
            Store_Format=None
            Acquisition_Ind='Automatic'
            Start_Date,End_Date=Invoice_Date,Invoice_Date
            Promotion_No,Product_No=None,None
            Quantity,Unit_Price=None,None
            try:
                lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind,"-"+Invoice_Totals_dict[Invoice_No]))
            except:
                Invoice_Description=None
                lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind,"-"+Invoice_Totals_dict[Invoice_No]))
            check_list.append(Invoice_No)
            Product_No=None
            date=None
        if Invoice_credited:
            Invoice_Description=Invoice_credited.group(1)
            Start_Date,End_Date=Invoice_Date,Invoice_Date
            Promotion_No,Product_No=None,None
            Quantity,Unit_Price=None,None
        if Case_move:
            Invoice_Description="Case Movement Charges"
            Start_Date,End_Date=Invoice_Date,Invoice_Date
            Promotion_No,Product_No=None,None
            Quantity,Unit_Price=None,None
        if "VOLUME REBATE" in line:
            Invoice_Description="Credit"
            Start_Date,End_Date=Invoice_Date,Invoice_Date
            Promotion_No,Product_No=None,None
            Quantity,Unit_Price=None,None
        if Deal_credited:
            Invoice_Description=Deal_credited.group(1)
            Start_Date,End_Date=Invoice_Date,Invoice_Date
            Promotion_No,Product_No=None,None
            Quantity,Unit_Price=None,None

#Checking the text and extracting the infomation required for invoices related to marketing
def Marketing_Information(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number):
    Start_Date,End_Date=Invoice_Date,Invoice_Date
    Promotion_No,Product_No=None,None
    Quantity,Unit_Price=None,None
    Net_Amount=Invoice_Totals_dict[Invoice_No]
    Store_Format=None
    Acquisition_Ind='Automatic'
    Invoice_Description="Look on Image"
    for line in text.split('\n'):
        line = " ".join(line.split())
        vat=VAT_Rate_Re.search(line)
        if vat:
            VAT_Rate=vat.group(1)
            if "20" in VAT_Rate:
                VAT_Rate=0.2
                Gross_Amount=float(Net_Amount)*1.2
            else:
                VAT_Rate=0
                Gross_Amount=float(Net_Amount)*1
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind,Invoice_Totals_dict[Invoice_No]))
            check_list.append(Invoice_No)

#Checking the text and extracting the infomation required for invoices related to Fixed Funding
Promo_re_1=re.compile(r'Agreement (\d+)')
#Regex for date
date_re_1=re.compile(r'^Billing Period (\d{2})/(\d{2})/(\d{4}) To (\d{2})/(\d{2})/(\d{4})')
#regex for VAT
VAT_re_1=re.compile(r'VAT Rate ([0-9%.]*)$')
#regex for Allowance
All_desc_re_1=re.compile(r'Allowance Description (.*)$')
def Fixed_Funding(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number):
    Product_No=None
    Quantity,Unit_Price=None,None
    Net_Amount=Invoice_Totals_dict[Invoice_No]
    Store_Format=None
    Acquisition_Ind='Automatic'
    for line in text.split('\n'):
        line = " ".join(line.split())
        promo=Promo_re_1.search(line)
        date=date_re_1.search(line)
        VAT=VAT_re_1.search(line)
        desc=All_desc_re_1.search(line)
        if promo:
            Promotion_No=promo.group(1)
        if date:
            Start_Date=date.group(1)+"/"+date.group(2)+"/"+date.group(3)
            End_Date=date.group(4)+"/"+date.group(5)+"/"+date.group(6)
        if VAT:
            VAT_Rate=VAT.group(1)
            if "20" in VAT_Rate:
                VAT_Rate=0.2
                Gross_Amount=float(Net_Amount)*1.2
            else:
                VAT_Rate=0
                Gross_Amount=float(Net_Amount)*1
        if desc:
            Invoice_Description=desc.group(1)
    lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind,Invoice_Totals_dict[Invoice_No]))
    check_list.append(Invoice_No)

#Checking the text and extracting the infomation required for invoices related to Miscellaneous charges
def Miscellaneous_Infomation(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number):
    Start_Date,End_Date=Invoice_Date,Invoice_Date
    Promotion_No,Product_No=None,None
    Quantity,Unit_Price=None,None
    Net_Amount=Invoice_Totals_dict[Invoice_No]
    Store_Format=None
    Acquisition_Ind='Automatic'
    Invoice_Description=Deal_Type+' Look on image'
    for line in text.split('\n'):
        line = " ".join(line.split())
        vat=VAT_Rate_Re.search(line)
        if vat:
            VAT_Rate=vat.group(1)
            if "20" in VAT_Rate:
                VAT_Rate=0.2
                Gross_Amount=float(Net_Amount)*1.2
            else:
                VAT_Rate=0
                Gross_Amount=float(Net_Amount)*1
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind,Invoice_Totals_dict[Invoice_No]))
            check_list.append(Invoice_No)

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

def data_extraction_ASDA(base_path):
    for filename in listdir_nohidden(base_path):
        print(base_path,filename)
        try:
            #print(filename)
            if filename=="desktop.ini":continue
            else:None
            text=Read_pdf(os.path.join(base_path,filename))
            SAL_Invoice_Type,Unit_Funding_Type,Deal_Type=Deal_Type_Check(os.path.join(base_path,filename),text)
            Invoice_No,Invoice_Date,Reference_Number=Invoice_infomation(text)
            if Debit_or_credit(text):
                if SAL_Invoice_Type=='PR':
                    Promo_Information(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number)
                elif SAL_Invoice_Type=='MK':
                    Marketing_Information(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number)
                elif SAL_Invoice_Type=='FX':
                    Fixed_Funding(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number)
                elif SAL_Invoice_Type=='MS':
                    Miscellaneous_Infomation(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number)
                else:
                    continue
            else:
                if SAL_Invoice_Type=='PR':
                    Credit_Information(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number)
                if SAL_Invoice_Type=='MS':
                    Credit_Misc_Information(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number)
            if Invoice_No in check_list:
                try:
                    os.rename(os.path.join(base_path,filename),os.path.join(base_path,filename))
                except:
                    os.replace(os.path.join(base_path,filename),os.path.join(base_path,filename))
            else:continue
        except:None
    return pd.DataFrame(lines)

def filter_list(list,inv_number):
    for a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u in list:
        if h == inv_number:
            yield h,p

def into_data_frame(lines):
    df=pd.DataFrame(lines)
    df.to_csv('Oli.csv',index=False)

###USER INPUT###
Salitix_Client_Number =""
Salitix_Customer_Number =""

######TESTING#####
#file for testing
#base_path=r'C:\Users\Python\Desktop\ASDA Images\Incomplete'
#data_extraction(base_path)
#into_data_frame(lines)
