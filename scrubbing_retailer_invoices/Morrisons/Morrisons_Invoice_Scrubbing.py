import os
from pathlib import Path
import re
import pdfplumber
import pandas as pd
from collections import namedtuple

Line = namedtuple('Line','Salitix_Client_Number Salitix_Customer_Number SAL_Invoice_type Unit_Funding_Type Reference_number Line_Description Deal_Type Invoice_No Invoice_Date Promotion_No Product_No Start_Date End_Date Quantity Unit_Price Net_Amount VAT_Rate Gross_Amount Store_Format Invoice_Description Acquisition_Ind')

Line2= namedtuple('Line2','Invoice_No Invoice_Total')
#This will be the Dataframe output...
lines=[]
Invoice_Totals_df=[]
check_list=[]
Invoice_Totals_dict={}
Gross_Total_dict={}
#referring for SAL codes...
SAL_CSV=pd.read_csv(r'C:\Users\Python\Desktop\projects\scrubbing_retailer_invoices\docs\Consistent Refrences for all clients\SAL_ref.csv')
description=pd.read_csv(r'C:\Users\Python\Desktop\projects\scrubbing_retailer_invoices\docs\Consistent Refrences for all clients\Line_desc_Morrisons.csv')

DEAL_CSV=pd.read_csv(r'C:\Users\Python\Desktop\projects\scrubbing_retailer_invoices\docs\Deal_Type_Check.csv')


VAT_CODE_dict={"Z":"0","A":"20","":"0","15.78":"1578","CO":"0","13.88":"1388"}

def Read_pdf(file):
    pdf_text=''
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            pdf_text+=text
    return pdf_text

Invoice_No_re=re.compile(r'Document Number: (.*)$')
Invoice_Date_re=re.compile(r'^Document Date: ([0-9/]*) Currency')
total_re=re.compile(r'Sub Total -([0-9,.]*) GBP$')
Promo_re=re.compile(r'^DEAL NO.: (\d+) Order')
credit_re=re.compile(r'Sub Total ([0-9,.]*) GBP$')
gross_re=re.compile(r'^Total -([0-9,.]*) GBP$')
def Invoice_infomation(text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        Inv=Invoice_No_re.search(line)
        Inv_Date=Invoice_Date_re.search(line)
        total=total_re.search(line)
        credit=credit_re.search(line)
        promo=Promo_re.search(line)
        gross=gross_re.search(line)
        if Inv:
            Invoice_No=Inv.group(1)
            if "DEAL" not in Invoice_No:
                Promotion_No=None
            Reference_Number=Invoice_No
            split_out=Invoice_No.split("-")
            Invoice_No=split_out[-1]
            Invoice_No=Invoice_No.replace("_","")
        if Inv_Date:
            Invoice_Date=Inv_Date.group(1)
        if total:
            Invoice_Total=total.group(1)
            Invoice_Total=Invoice_Total.replace(",","")
        elif credit:
            Invoice_Total="-"+credit.group(1)
            Invoice_Total=Invoice_Total.replace(",","")
        if promo:
            Promotion_No=promo.group(1)
        if gross:
            Gross_Amount=gross.group(1)
    Invoice_Totals_df.append(Line2(Invoice_No,Invoice_Total))
    Invoice_Totals_dict[Invoice_No]=Invoice_Total
    Gross_Total_dict[Invoice_No]=Gross_Amount
    return Invoice_No,Invoice_Date,Reference_Number,Promotion_No

SAL_re=re.compile(r'Deal type (.*)$')
def Deal_Type_Check(file,text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        SAL=SAL_re.search(line)
        if SAL:
            Deal_Type=SAL.group(1)
            #print(Deal_Type)
            Start=DEAL_CSV.loc[DEAL_CSV['Deal_type']==Deal_Type]
            SAL_ref=Start['INV_ref'].iloc[0]
            Unit_ref=Start['Unit_ref'].iloc[0]
            return SAL_ref,Unit_ref,Deal_Type
        else:
            Deal_Type="BLANK"
            SAL_ref="MS"
            Unit_ref=""
    return SAL_ref,Unit_ref,Deal_Type

Line_Description=None
Invoice_Description=None
Acquisition_Ind='Automatic'
billing_date_re=re.compile(r'^Billing period ([0-9/]*) ([0-9/]*) Deal')
full_promo_line_re=re.compile(r'^(\d+) (\d+) (.*) ([0-9,.-]*) ([0-9,.]*) ([-0-9,.]*) (.*) ([AZ15.78CO83]*)$')
no_desc_promo_line_re=re.compile(r'^(\d+) (\d+) ([0-9,.-]*) ([0-9,.]*) ([-0-9,.]*) (.*) ([AZ15.78CO38]*)$')
no_store_promo_line_re=re.compile(r'^(\d+) (\d+) (.*) ([0-9,.-]*) ([0-9,.]*) ([-0-9,.]*) ([AZ15.78CO38]*)$')
no_desc_store_promo_line_re=re.compile(r'^(\d+) (\d+) ([0-9,.-]*) ([0-9,.]*) ([-0-9,.]*) ([AZ15.78CO38]*)$')
def Promotional_Infomation(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number,Promotion_No):
    group=[]
    for line in text.split('\n'):
        line = " ".join(line.split())
        group.append(line)
        billing_date=billing_date_re.search(line)
        full_promo_line=full_promo_line_re.search(line)
        no_desc_promo_line=no_desc_promo_line_re.search(line)
        no_store_promo_line=no_store_promo_line_re.search(line)
        no_desc_store_promo_line=no_desc_store_promo_line_re.search(line)
        if billing_date:
            Start_Date=billing_date.group(1)
            End_Date=billing_date.group(2)
        if no_desc_store_promo_line:
            Product_No=no_desc_store_promo_line.group(2)
            Invoice_Description=no_desc_store_promo_line.group(1)
            Quantity=no_desc_store_promo_line.group(3)
            Quantity=Quantity.replace("-","")
            Unit_Price=no_desc_store_promo_line.group(4)
            Net_Amount=no_desc_store_promo_line.group(5)
            Net_Amount=Net_Amount.replace(",","")
            Net_Amount=Net_Amount.replace("-","")
            Store_Format=group[-2]
            if "Morrisons DotCom" in group[-2]:
                Store_Format="Morrisons DotCom Store Pick"
            elif "Morrisons at Amazon" in group[-2]:
                Store_Format="Morrisons at Amazon Store Pick"
            elif "Morrisons Franchise" in group[-2]:
                Store_Format="Morrisons Franchise Store Pick"
            elif "Wholesale Bulk" in group[-2]:
                Store_Format="Wholesale Bulk Store Pick"
            VAT_CODE=no_desc_store_promo_line.group(6)
            VAT_Rate=VAT_CODE_dict[VAT_CODE]
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Product_No=None
            Invoice_Description=None
        elif no_store_promo_line:
            Product_No=no_store_promo_line.group(2)
            Invoice_Description=no_store_promo_line.group(1)
            Quantity=no_store_promo_line.group(4)
            Quantity=Quantity.replace("-","")
            Unit_Price=no_store_promo_line.group(5)
            Net_Amount=no_store_promo_line.group(6)
            Net_Amount=Net_Amount.replace(",","")
            Net_Amount=Net_Amount.replace("-","")
            Store_Format=group[-2]+" Store Pick"
            VAT_CODE=no_store_promo_line.group(7)
            VAT_Rate=VAT_CODE_dict[VAT_CODE]
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Product_No=None
        elif no_desc_promo_line:
            Product_No=no_desc_promo_line.group(2)
            Invoice_Description=no_desc_promo_line.group(1)
            Quantity=no_desc_promo_line.group(3)
            Quantity=Quantity.replace("-","")
            Unit_Price=no_desc_promo_line.group(4)
            Net_Amount=no_desc_promo_line.group(5)
            Net_Amount=Net_Amount.replace(",","")
            Net_Amount=Net_Amount.replace("-","")
            Store_Format=no_desc_promo_line.group(6)
            VAT_CODE=no_desc_promo_line.group(7)
            VAT_Rate=VAT_CODE_dict[VAT_CODE]
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Product_No=None
        elif full_promo_line:
            Product_No=full_promo_line.group(2)
            Invoice_Description=full_promo_line.group(1)
            Quantity=full_promo_line.group(4)
            Quantity=Quantity.replace("-","")
            Unit_Price=full_promo_line.group(5)
            Net_Amount=full_promo_line.group(6)
            Net_Amount=Net_Amount.replace(",","")
            Net_Amount=Net_Amount.replace("-","")
            Store_Format=full_promo_line.group(7)
            VAT_CODE=full_promo_line.group(8)
            VAT_Rate=VAT_CODE_dict[VAT_CODE]
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Product_No=None

v_full_promo_line_re=re.compile(r'^(\d+) (\d+) [A-Za-z](.*)[A-Za-z] ([0-9,.]*) ([-0-9,.]*) ([A-Za-z]*) ([AZ15.78CO83]*)$')
v_no_desc_promo_line_re=re.compile(r'^(\d+) (\d+) ([0-9,.-]*) ([-0-9,.]*) ([A-Za-z]*) ([AZ15.78CO38]*)$')
v_no_store_promo_line_re=re.compile(r'^(\d+) (\d+) [A-Za-z](.*)[A-Za-z] ([0-9,.]*) ([-0-9,.]*) ([AZ15.78CO38]*)$')
v_no_desc_store_promo_line_re=re.compile(r'^(\d+) (\d+) ([0-9,.]*) ([-0-9,.]*) ([AZ15.78CO38]*)$')
contribution_perc_re=re.compile(r'Contribution Percentage ([0-9.]*)%')
def Vendor_Promo_Information(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number,Promotion_No):
    group=[]
    for line in text.split('\n'):
        line = " ".join(line.split())
        group.append(line)
        billing_date=billing_date_re.search(line)
        full_promo_line=v_full_promo_line_re.search(line)
        no_desc_promo_line=v_no_desc_promo_line_re.search(line)
        no_store_promo_line=v_no_store_promo_line_re.search(line)
        no_desc_store_promo_line=v_no_desc_store_promo_line_re.search(line)
        contribution_perc=contribution_perc_re.search(line)
        full_promo_line2=full_promo_line_re.search(line)
        no_desc_promo_line2=no_desc_promo_line_re.search(line)
        no_store_promo_line2=no_store_promo_line_re.search(line)
        no_desc_store_promo_line2=no_desc_store_promo_line_re.search(line)
        if billing_date:
            Start_Date=billing_date.group(1)
            End_Date=billing_date.group(2)
        if contribution_perc:
            Unit_Price=contribution_perc.group(1)+"%"
        if no_desc_store_promo_line:
            Product_No=no_desc_store_promo_line.group(2)
            Invoice_Description=no_desc_store_promo_line.group(1)
            Quantity=no_desc_store_promo_line.group(3)
            Quantity=Quantity.replace("-","")
            Net_Amount=no_desc_store_promo_line.group(4)
            Net_Amount=Net_Amount.replace(",","")
            Net_Amount=Net_Amount.replace("-","")
            Store_Format=group[-2]
            if "Morrisons DotCom" in group[-2]:
                Store_Format="Morrisons DotCom Store Pick"
            elif "Morrisons at Amazon" in group[-2]:
                Store_Format="Morrisons at Amazon Store Pick"
            elif "Morrisons Franchise" in group[-2]:
                Store_Format="Morrisons Franchise Store Pick"
            elif "Wholesale Bulk" in group[-2]:
                Store_Format="Wholesale Bulk Store Pick"
            VAT_CODE=no_desc_store_promo_line.group(5)
            VAT_Rate=VAT_CODE_dict[VAT_CODE]
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Invoice_Description=None
            Product_No=None
        elif no_store_promo_line:
            Product_No=no_store_promo_line.group(2)
            Invoice_Description=no_store_promo_line.group(1)
            Quantity=no_store_promo_line.group(4)
            Quantity=Quantity.replace("-","")
            Net_Amount=no_store_promo_line.group(5)
            Net_Amount=Net_Amount.replace(",","")
            Net_Amount=Net_Amount.replace("-","")
            Store_Format=group[-2]+" Store Pick"
            VAT_CODE=no_store_promo_line.group(6)
            VAT_Rate=VAT_CODE_dict[VAT_CODE]
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Invoice_Description=None
            Product_No=None
        elif no_desc_promo_line:
            Product_No=no_desc_promo_line.group(2)
            Invoice_Description=no_desc_promo_line.group(1)
            Quantity=no_desc_promo_line.group(3)
            Quantity=Quantity.replace("-","")
            Net_Amount=no_desc_promo_line.group(4)
            Net_Amount=Net_Amount.replace(",","")
            Net_Amount=Net_Amount.replace("-","")
            Store_Format=no_desc_promo_line.group(5)
            VAT_CODE=no_desc_promo_line.group(6)
            VAT_Rate=VAT_CODE_dict[VAT_CODE]
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Product_No=None
            Invoice_Description=None
        elif full_promo_line:
            Product_No=full_promo_line.group(2)
            Invoice_Description=full_promo_line.group(1)
            Quantity=full_promo_line.group(4)
            Quantity=Quantity.replace("-","")
            Net_Amount=full_promo_line.group(5)
            Net_Amount=Net_Amount.replace(",","")
            Net_Amount=Net_Amount.replace("-","")
            Store_Format=full_promo_line.group(6)
            VAT_CODE=full_promo_line.group(7)
            VAT_Rate=VAT_CODE_dict[VAT_CODE]
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Product_No=None
            Invoice_Description=None
        elif no_desc_store_promo_line2:
            Product_No=no_desc_store_promo_line2.group(2)
            Invoice_Description=no_desc_store_promo_line2.group(1)
            Quantity=no_desc_store_promo_line2.group(3)
            Quantity=Quantity.replace("-","")
            Unit_Price=no_desc_store_promo_line2.group(4)
            Net_Amount=no_desc_store_promo_line2.group(5)
            Net_Amount=Net_Amount.replace(",","")
            Net_Amount=Net_Amount.replace("-","")
            Store_Format=group[-2]
            if "Morrisons DotCom" in group[-2]:
                Store_Format="Morrisons DotCom Store Pick"
            elif "Morrisons at Amazon" in group[-2]:
                Store_Format="Morrisons at Amazon Store Pick"
            elif "Morrisons Franchise" in group[-2]:
                Store_Format="Morrisons Franchise Store Pick"
            elif "Wholesale Bulk" in group[-2]:
                Store_Format="Wholesale Bulk Store Pick"
            VAT_CODE=no_desc_store_promo_line2.group(6)
            VAT_Rate=VAT_CODE_dict[VAT_CODE]
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Product_No=None
            Invoice_Description=None
        elif no_store_promo_line2:
            Product_No=no_store_promo_line2.group(2)
            Invoice_Description=no_store_promo_line2.group(1)
            Quantity=no_store_promo_line2.group(4)
            Quantity=Quantity.replace("-","")
            Unit_Price=no_store_promo_line2.group(5)
            Net_Amount=no_store_promo_line2.group(6)
            Net_Amount=Net_Amount.replace(",","")
            Net_Amount=Net_Amount.replace("-","")
            Store_Format=group[-2]+" Store Pick"
            VAT_CODE=no_store_promo_line2.group(7)
            VAT_Rate=VAT_CODE_dict[VAT_CODE]
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Product_No=None
            Invoice_Description=None
        elif no_desc_promo_line2:
            Product_No=no_desc_promo_line2.group(2)
            Invoice_Description=no_desc_promo_line2.group(1)
            Quantity=no_desc_promo_line2.group(3)
            Quantity=Quantity.replace("-","")
            Unit_Price=no_desc_promo_line2.group(4)
            Net_Amount=no_desc_promo_line2.group(5)
            Net_Amount=Net_Amount.replace(",","")
            Net_Amount=Net_Amount.replace("-","")
            Store_Format=no_desc_promo_line2.group(6)
            VAT_CODE=no_desc_promo_line2.group(7)
            VAT_Rate=VAT_CODE_dict[VAT_CODE]
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Product_No=None
            Invoice_Description=None
        elif full_promo_line2:
            Product_No=full_promo_line2.group(2)
            Invoice_Description=full_promo_line2.group(1)
            Quantity=full_promo_line2.group(4)
            Quantity=Quantity.replace("-","")
            Unit_Price=full_promo_line2.group(5)
            Net_Amount=full_promo_line2.group(6)
            Net_Amount=Net_Amount.replace(",","")
            Net_Amount=Net_Amount.replace("-","")
            Store_Format=full_promo_line2.group(7)
            VAT_CODE=full_promo_line2.group(8)
            VAT_Rate=VAT_CODE_dict[VAT_CODE]
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Product_No=None
            Invoice_Description=None


def Marketing_Information(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number,Promotion_No):
    Start_Date,End_Date=Invoice_Date,Invoice_Date
    Product_No=None
    Quantity,Unit_Price=None,None
    Net_Amount=Invoice_Totals_dict[Invoice_No]
    Gross_Amount=Gross_Total_dict[Invoice_No].replace(",","")
    if Net_Amount==Gross_Amount:
        VAT_Rate='0'
    else:
        VAT_Rate=(float(Gross_Amount)/float(Net_Amount))-1
        if abs(VAT_Rate-0.2)<=0.05:
            VAT_Rate='20'
        else:
            VAT_Rate='Look'
    Store_Format=None
    Acquisition_Ind='Automatic'
    Invoice_Description="Look on Image"
    lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
    check_list.append(Invoice_No)

prod_number_re=re.compile(r'^(\d+) (\d+) MIN: (.*) -([0-9,.]*) (.*)([AZ15.78CO38]*)$')
def Miscellaneous_Information(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number,Promotion_No):
    Product_No=None
    for line in text.split('\n'):
        line = " ".join(line.split())
        prod_number=prod_number_re.search(line)
        if prod_number:
            Product_No=prod_number.group(2)
    Start_Date,End_Date=Invoice_Date,Invoice_Date
    Quantity,Unit_Price=None,None
    Net_Amount=Invoice_Totals_dict[Invoice_No]
    Gross_Amount=Gross_Total_dict[Invoice_No].replace(",","")
    if Net_Amount==Gross_Amount:
        VAT_Rate='0'
    else:
        VAT_Rate=(float(Gross_Amount)/float(Net_Amount))-1
        if abs(VAT_Rate-0.2)<=0.05:
            VAT_Rate='20'
        else:
            VAT_Rate='Look'
    Store_Format=None
    Acquisition_Ind='Automatic'
    Invoice_Description="Look on Image"
    lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
    check_list.append(Invoice_No)

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

def data_extraction_morrisons(base_path):
    for filename in listdir_nohidden(base_path):
        try:
            print(filename)
            if filename=="desktop.ini":continue
            elif filename=="T&C.pdf":continue
            else:None
            text=Read_pdf(os.path.join(base_path,filename))
            SAL_Invoice_Type,Unit_Funding_Type,Deal_Type=Deal_Type_Check(os.path.join(base_path,filename),text)
            #print(SAL_Invoice_Type)
            Invoice_No,Invoice_Date,Reference_Number,Promotion_No=Invoice_infomation(text)
            if SAL_Invoice_Type=='PR':
                if Deal_Type=="COMPLEX DEAL - Vendor Funded Promotion":
                    Vendor_Promo_Information(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number,Promotion_No)
                else:
                    Promotional_Infomation(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number,Promotion_No)
            elif SAL_Invoice_Type=='MK':
                Marketing_Information(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number,Promotion_No)
            elif SAL_Invoice_Type=='MS':
                Miscellaneous_Information(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number,Promotion_No)
            invoice_integrity(Invoice_No,list(filter_list(lines,Invoice_No)))
            if Invoice_No in check_list:
                try:
                    os.rename(os.path.join(base_path,filename),os.path.join(base_path,filename))
                except:
                    os.replace(os.path.join(base_path,filename),os.path.join(base_path,filename))
            else:continue
        except:continue
    return pd.DataFrame(lines)

def filter_list(list,inv_number):
    for a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u in list:
        if h == inv_number:
            yield h,p

def invoice_integrity(Invoice_No,list):
    total=0
    for i in list:
        total+=float(i[1])
    if abs(total-float(Invoice_Totals_dict[Invoice_No]))>5:
        check_list.remove(Invoice_No)

def into_data_frame(lines):
    df=pd.DataFrame(lines)
    df.to_csv('Oli.csv',index=False)

###USER INPUT###
Salitix_Client_Number ="CL002"
Salitix_Customer_Number ="MOR01"

#####TESTING#####
#file for testing
#base_path=r'C:\Users\Python\Desktop\Morrisons test\Incomplete'
#data_extraction_morrisons(base_path)
#into_data_frame(lines)
