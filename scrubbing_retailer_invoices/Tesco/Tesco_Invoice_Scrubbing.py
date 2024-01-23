import os
from pathlib import Path
#Below for regular expression analysis
import re
#Below is what reads the pdf page by page and stores it as a variable
import pdfplumber
import pandas as pd
from collections import namedtuple

#This will be the names of the columns that from the DataFrame.
Line = namedtuple('Line','Salitix_Client_Number Salitix_Customer_Number SAL_Invoice_Type Unit_Funding_Type Reference_Number Line_Description Deal_Type Invoice_No Invoice_Date Promotion_No Product_No Start_Date End_Date Quantity Unit_Price Net_Amount VAT_Rate Gross_Amount Store_Format Invoice_Description Acquisition_Ind')
#Dictionary below to assign the invoice total to the invoice.
Line2= namedtuple('Line2','Invoice_No Invoice_Total')
#THis will be the Dataframe output...
lines=[]
Invoice_Totals_df=[]
check_list=[]
Invoice_Totals_dict={}

Line_Description=""
'''Change below as directories change'''
#Tesco calender to match week numbers to Start Date and End date of a promotion.
Calender=pd.read_csv(r'C:\Users\Python\Desktop\projects\scrubbing_retailer_invoices\docs\Tesco Week Calendar 201501-202452.csv')
#This is to reference codes we use in the SCC for invoice types.
SAL_CSV=pd.read_csv(r'C:\Users\Python\Desktop\projects\scrubbing_retailer_invoices\docs\Consistent Refrences for all clients\SAL_ref.csv')
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
        if line == "CREDIT NOTE":
            return False
        elif line == "INVOICE":
            return True

#RegEx for the Deal type on the pdf.
SAL_re=re.compile(r'Deal(\s?)Type(.*): (.*)')
SAL_re_empty=re.compile(r'Deal(\s?)Type(.*):')
#Checking the text and outputting the deal types.
def Deal_Type_Check(file,text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        #print(line)
        SAL=SAL_re.search(line)
        SAL_blank=SAL_re_empty.search(line)
        if SAL:
            Deal_Type=SAL.group(3)
           # print(Deal_Type)
            Start=DEAL_CSV.loc[DEAL_CSV['Deal_type']==Deal_Type]
            SAL_ref=Start['INV_ref'].iloc[0]
            Unit_ref=Start['Unit_ref'].iloc[0]
        elif SAL_blank and not SAL:
            Deal_Type="BLANK"
            SAL_ref="MS"
            Unit_ref=""
    return SAL_ref,Unit_ref,Deal_Type

#Regex for invoice infomation
Invoice_No_re=re.compile(r'Invoice(.*)No(.*):(.*)')
Invoice_Date_re=re.compile(r'Invoice(.*)Date(.*):(\d{4})-(\d{2})-(\d{2})')
reference_re=re.compile(r'Reference#(.*):(\s?)(.*)')
total_re=re.compile(r'Total(\s?)[{(][GBPEUR]*[})](\s?)(.*)(\s)(.*)(\s)(.*)$')

credit_re=re.compile(r'Credit Note No :(\d+)$')
credit_Date_re=re.compile(r'Credit Note Date(.*):(\d{4})-(\d{2})-(\d{2})')
#Checking the text and outputting the Invoice Info.
def Invoice_infomation(text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        Inv=Invoice_No_re.search(line)
        Inv_Date=Invoice_Date_re.search(line)
        ref=reference_re.search(line)
        total=total_re.search(line)
        credit=credit_re.search(line)
        credit_date=credit_Date_re.search(line)
        if Inv:
            Invoice_No=Inv.group(3)
            Invoice_No=Invoice_No.replace(" ","")
        if credit:
            Invoice_No=credit.group(1)
            Invoice_No=Invoice_No.replace(" ","")
        if Inv_Date:
            Invoice_Date=Inv_Date.group(5)+'/'+Inv_Date.group(4)+'/'+Inv_Date.group(3)
        if credit_date:
            Invoice_Date=credit_date.group(4)+'/'+credit_date.group(3)+'/'+credit_date.group(2)
        if ref:
            Reference_Number=ref.group(3)
        if total:
            Invoice_Total=total.group(3)
            Invoice_Total=Invoice_Total.replace(",","")
    Invoice_Totals_df.append(Line2(Invoice_No,Invoice_Total))
    Invoice_Totals_dict[Invoice_No]=Invoice_Total
    return Invoice_No,Invoice_Date,Reference_Number

#Regex for Retro Epos Promotions.
Promo_re=re.compile(r'tion ID (.*) [-] ([0-9,.]*) ([0-9,.]*) ([0-9,.]*) ([0-9,.]*) ([0-9,.]*) ([0-9,.]*)$')
Promo_blankvat_re=re.compile(r'tion ID (.*) [-] ([0-9,.]*) ([0-9,.]*) ([0-9,.]*) ([0-9,.]*)$')
Promo_no_text_re=re.compile(r'^(\d+)-(.*) ([0-9,.]*) ([0-9,.]*) ([0-9,.]*) ([0-9,.]*) ([0-9,.]*) ([0-9,.]*)$')
#Regex for product number
Product_re=re.compile(r'[-]?(\s)?(\d{7,10})(\s)?[-]?')
#Regex for date
date_re=re.compile(r'[-]?(\s?)20(\d{4})$')
#Checking the text and outputting the line level promo info.
def Promo_Information(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number):
    for line in text.split('\n'):
        line = " ".join(line.split())
        promo=Promo_re.search(line)
        Promo_blankvat=Promo_blankvat_re.search(line)
        promo_no_text=Promo_no_text_re.search(line)
        prod=Product_re.search(line)
        date=date_re.search(line)
        if promo:
            Promotion_No=promo.group(1)
            Quantity=promo.group(2)
            Unit_Price=promo.group(3)
            Net_Amount=promo.group(4)
            Net_Amount=Net_Amount.replace(",","")
            VAT_Rate=promo.group(5)
            VAT_Rate=VAT_Rate.replace(".","")
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            VAT_Rate="0."+VAT_Rate
        elif Promo_blankvat and not promo:
            Promotion_No=Promo_blankvat.group(1)
            Quantity=Promo_blankvat.group(2)
            Unit_Price=Promo_blankvat.group(3)
            Net_Amount=Promo_blankvat.group(4)
            Net_Amount=Net_Amount.replace(",","")
            VAT_Rate='0'
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
        elif prod:
            Product_No=prod.group(2)
            date=None
        if date and Product_No:
            timeline=int("20"+date.group(2))
            Start=Calender.loc[Calender['Week']==timeline]
            Start_Date=Start['Start'].iloc[0]
            End_Date=Start['End'].iloc[0]
            Store_Format,Invoice_Description,Acquisition_Ind=None,None,'Automatic'
            if VAT_Rate !='0' or VAT_Rate != '0.20' : VAT_Rate=20
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Product_No=None
            date=None

date_2_re=re.compile(r'Tesco Promo Week :(\s?)(\d{4})-wk(\d{2})$')
Promo_no_text_re=re.compile(r'^(\d+)-(.*) ([0-9,.]*) ([0-9,.]*) ([0-9,.]*) ([0-9,.]*) ([0-9,.]*) ([0-9,.]*)$')
def Promo_information_2020(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number):
    Promotion_No=None
    count=0
    text_desc=text.split('\n')
    for line in text.split('\n'):
        count+=1
        line = " ".join(line.split())
        promo_no_text=Promo_no_text_re.search(line)
        promo_no_2_text=Promo_no_text_re.search(line)
        prod=Product_re.search(line)
        date=date_2_re.search(line)
        if prod and promo_no_text:
            promo_desc=promo_no_text.group(2)
            Promotion_No=promo_no_text.group(1)
            Quantity=promo_no_text.group(3)
            Unit_Price=promo_no_text.group(4)
            Net_Amount=promo_no_text.group(5)
            Net_Amount=Net_Amount.replace(",","")
            VAT_Rate=promo_no_text.group(6)
            VAT_Rate=VAT_Rate.replace(".","")
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            VAT_Rate="0."+VAT_Rate
            Product_No=prod.group(2)
            if Product_No==Promotion_No:
                continue
            #This is to bring in Store and promo description.
            Full_desc=Promotion_No+"-"+promo_no_text.group(2)+" "+text[count-1]+" "+text[count]+" "+text[count+1]+" "+text[count+2]
            result1=re.search("-(.*)-",Full_desc)
            result2=re.search("salessluppierid (\d+) - (\w+)")
            Store_Format,Invoice_Description,Acquisition_Ind=result1.group(1),result2.group(2),'Automatic'
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Promotion_No=None
        elif promo_no_text:
            Promotion_No=promo_no_text.group(1)
            Quantity=promo_no_text.group(3)
            Unit_Price=promo_no_text.group(4)
            Net_Amount=promo_no_text.group(5)
            Net_Amount=Net_Amount.replace(",","")
            VAT_Rate=promo_no_text.group(6)
            VAT_Rate=VAT_Rate.replace(".","")
            Gross_Amount=str(float(Net_Amount)*float("1."+VAT_Rate))
            VAT_Rate="0."+VAT_Rate
            promo_desc=promo_no_text.group(2)
        elif date:
            timeline=int(date.group(2)+date.group(3))
            Start=Calender.loc[Calender['Week']==timeline]
            Start_Date=Start['Start'].iloc[0]
            End_Date=Start['End'].iloc[0]
        elif prod and Promotion_No:
            Product_No=prod.group(2)
            Full_desc=Promotion_No+"-"+promo_desc+text_desc[count-1]+text_desc[count]+text_desc[count+1]+text_desc[count+2]+text_desc[count+3]#
            Full_desc=Full_desc.replace("Company Registered in England. Registered Office: Tesco House, Shire Park, Kestrel Way, Welwyn Garden City, AL7 1GA","")
            #print(Full_desc)
            result1=re.search("(\d+)-(.*)-(\d+)",Full_desc)
            try:
                Invoice_Description=result1.group(2)
            except:
                try:
                    Full_desc=Promotion_No+"-"+promo_desc+" "+text_desc[count-2]+text_desc[count-1]+text_desc[count]+text_desc[count+1]+text_desc[count+2]+text_desc[count+3]
                    Full_desc=Full_desc.replace("Company Registered in England. Registered Office: Tesco House, Shire Park, Kestrel Way, Welwyn Garden City, AL7 1GA","")
                   # print(Full_desc)
                    result1=re.search("(\d+)-(.*)-(\d+)",Full_desc)
                    Invoice_Description=result1.group(2)
                except:
                    Full_desc=Promotion_No+"-"+promo_desc+" "+text_desc[count-3]+text_desc[count-2]+text_desc[count-1]+text_desc[count]+text_desc[count+1]+text_desc[count+2]+text_desc[count+3]
                    Full_desc=Full_desc.replace("Company Registered in England. Registered Office: Tesco House, Shire Park, Kestrel Way, Welwyn Garden City, AL7 1GA","")
                   # print(Full_desc)
                    result1=re.search("(\d+)-(.*)-([ ]*)?(\d+)",Full_desc)
                    Invoice_Description=result1.group(2)
            Store_Format,Acquisition_Ind='Main','Automatic'
            lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
            check_list.append(Invoice_No)
            Promotion_No=None

#Checking the text and extracting the infomation required for invoices related to marketing

def Marketing_Information(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number):
    Start_Date,End_Date=Invoice_Date,Invoice_Date
    Promotion_No,Product_No=None,None
    Quantity,Unit_Price=None,None
    Net_Amount=Invoice_Totals_dict[Invoice_No]
    for line in text.split('\n'):
        line = " ".join(line.split())
        total=total_re.search(line)
        if total:
            Gross_Amount=total.group(7)
            Gross_Amount=Gross_Amount.replace(",","")
            break
    if Gross_Amount==Net_Amount:VAT_Rate='0'
    else: VAT_Rate='0.2'
    Store_Format=None
    Acquisition_Ind='Automatic'
    Invoice_Description="Look on Image"
    lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
    check_list.append(Invoice_No)

#Checking the text and extracting the infomation required for invoices related to Fixed Funding
def Fixed_Funding(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number):
    Start_Date,End_Date=Invoice_Date,Invoice_Date
    Promotion_No,Product_No=None,None
    Quantity,Unit_Price=None,None
    Net_Amount=Invoice_Totals_dict[Invoice_No]
    for line in text.split('\n'):
        line = " ".join(line.split())
        total=total_re.search(line)
        if total:
            Gross_Amount=total.group(7)
            Gross_Amount=Gross_Amount.replace(",","")
            break
    if Gross_Amount==Net_Amount:VAT_Rate='0'
    else: VAT_Rate='0.2'
    Store_Format=None
    Acquisition_Ind='Automatic'
    Invoice_Description=Deal_Type+' Look on image'
    lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
    check_list.append(Invoice_No)

#Checking the text and extracting the infomation required for invoices related to Miscellaneous charges
def Miscellaneous_Infomation(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number):
    Start_Date,End_Date=Invoice_Date,Invoice_Date
    Promotion_No,Product_No=None,None
    Quantity,Unit_Price=None,None
    Net_Amount=Invoice_Totals_dict[Invoice_No]
    for line in text.split('\n'):
        line = " ".join(line.split())
        total=total_re.search(line)
        if total:
            Gross_Amount=total.group(7)
            Gross_Amount=Gross_Amount.replace(",","")
            break
    if Gross_Amount==Net_Amount:VAT_Rate='0'
    else: VAT_Rate='0.2'
    Store_Format=None
    Acquisition_Ind='Automatic'
    Invoice_Description=Deal_Type+' Look on image'
    lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
    check_list.append(Invoice_No)

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

def data_extraction_Tesco(base_path):
    for filename in listdir_nohidden(base_path):
        try:
            if filename=="desktop.ini":continue
            else:None
            text=Read_pdf(os.path.join(base_path,filename))
            SAL_Invoice_Type,Unit_Funding_Type,Deal_Type=Deal_Type_Check(os.path.join(base_path,filename),text)
            Invoice_No,Invoice_Date,Reference_Number=Invoice_infomation(text)
            if Debit_or_credit(text):
                if SAL_Invoice_Type=='PR':
                    Promo_Information(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number)
                    if Invoice_No not in check_list:
                        Promo_information_2020(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number)
                elif SAL_Invoice_Type=='MK':
                    Marketing_Information(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number)
                elif SAL_Invoice_Type=='FX':
                    Fixed_Funding(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number)
                elif SAL_Invoice_Type=='MS':
                    Miscellaneous_Infomation(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number)
                else:
                    continue
                invoice_integrity(Invoice_No,list(filter_list(lines,Invoice_No)))
            else:
                Credit_Information(text,os.path.join(base_path,filename),SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number)
            if Invoice_No in check_list:
                try:
                    os.rename(os.path.join(base_path,filename),os.path.join(base_path,Invoice_No+".pdf"))
                except:
                    os.replace(os.path.join(base_path,filename),os.path.join(base_path,Invoice_No+".pdf"))
            else:continue
        except:None
    return pd.DataFrame(lines)

def filter_list(list,inv_number):
    for a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u in list:
        if h == inv_number:
            yield h,p

def invoice_integrity(Invoice_No,list):
    total=0
    for i in list:
        total+=float(i[1])
   # print(float(Invoice_Totals_dict[Invoice_No]))
    if abs(total-float(Invoice_Totals_dict[Invoice_No]))>5:
        check_list.remove(Invoice_No)

Promo_no_text_re=re.compile(r'^(\d+)-(.*) ([0-9,.-]*) ([0-9,.-]*) ([0-9,.-]*) ([0-9,.-]*) ([0-9,.-]*) ([0-9,.-]*)$')
def Credit_Information(text,file,SAL_Invoice_Type,Unit_Funding_Type,Deal_Type,Invoice_No,Invoice_Date,Reference_Number):
    Start_Date,End_Date=Invoice_Date,Invoice_Date
    Promotion_No,Product_No=None,None
    Quantity,Unit_Price=None,None
    Net_Amount=Invoice_Totals_dict[Invoice_No]
    for line in text.split('\n'):
        line = " ".join(line.split())
        total=total_re.search(line)
        if total:
            Gross_Amount=total.group(7)
            break
    if float(abs(Gross_Amount))==float(abs(Net_Amount)):VAT_Rate='0'
    else: VAT_Rate='20'
    Gross_Amount=Net_Amount
    Store_Format=None
    Acquisition_Ind='Automatic'
    Invoice_Description=Deal_Type+' Look on image'
    lines.append(Line(Salitix_Client_Number,Salitix_Customer_Number,SAL_Invoice_Type,Unit_Funding_Type,Reference_Number,Line_Description,Deal_Type,Invoice_No,Invoice_Date,Promotion_No,Product_No,Start_Date,End_Date,Quantity,Unit_Price,Net_Amount,VAT_Rate,Gross_Amount,Store_Format,Invoice_Description,Acquisition_Ind))
    check_list.append(Invoice_No)


def into_data_frame(lines):
    df=pd.DataFrame(lines)
    df.to_csv('Oli.csv',index=False)

###USER INPUT###
Salitix_Client_Number ="CL012"
Salitix_Customer_Number ="TES01"

######TESTING#####
#file for testing
#base_path=r'C:\Users\Python\Desktop\Tesco test\Incomplete'
#data_extraction_Tesco(base_path)
#into_data_frame(lines)
