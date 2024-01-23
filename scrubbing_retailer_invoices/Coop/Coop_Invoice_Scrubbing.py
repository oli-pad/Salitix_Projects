import pytesseract
from PIL import Image
import os
import re
import pdfplumber
from collections import namedtuple
import sys
import pandas as pd


pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Python\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

Line = namedtuple('Line','Salitix_Client_Number Salitix_Customer_Number SAL_Invoice_type Unit_Funding_Type Line_Description Deal_Type Invoice_No Invoice_Date Promotion_No Product_No Week Period Year Start_Date End_Date Quantity Unit_Price Net_Amount VAT_Amount Gross_Amount Store_Format Invoice_Description Acquisition_Ind')

TCGLine = namedtuple('TCGLine','Promotion_No TCG_qty FRTS_qty FRTS_Percentage Invoice_Count')


Calendar_df=pd.read_csv(r'C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\Coop\COOP_Calendar_Pladis.csv')

def tiff_to_txt(tiff_path: str) -> str:
    image = Image.open(tiff_path)
    text = pytesseract.image_to_string(image)
    return text

def Read_pdf(file):
    pdf_text=''
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            pdf_text+=text
    return pdf_text

def listdir_nohidden(path):
    for f in os.listdir(path):
        if ".tif" in f:
            if not f.startswith('.'):
                yield f

def listdir_nohidden_pdf(path):
    for f in os.listdir(path):
        if ".pdf" in f:
            if not f.startswith('.'):
                yield f

def run_through_files(base_path):
    Coop_Invoice_Scrubbing=[]
    prev_df=pd.read_excel(r'W:\Audit\Pladis\Invoice Images\EmailStagingBay\CoOp\Coop_Invoice_Scrubbing1.xlsx')
    file_list=prev_df['Invoice_No'].tolist()
    print(file_list)
    #for file in listdir_nohidden(base_path):
    #    try:
    #        if file.replace('.tif','') in file_list:
    #            continue
    #        Coop_Invoice_Scrubbing.append(Coop_Invoice(os.path.join(base_path,file)).line)
    #        df=pd.DataFrame(Coop_Invoice_Scrubbing)
    #        df=pd.concat([prev_df,df])
    #        df.to_excel(base_path+'//'+'Coop_Invoice_Scrubbing1.xlsx',index=False)
    #    except:
    #        print(file)
    #        continue
    FRTS_VS_TCG(prev_df,base_path)

class Coop_Invoice:

    def __init__(self, filename):
        self.filename = filename
        self.text = tiff_to_txt(filename) if filename.endswith('.tif') else Read_pdf(filename)
        self.lines = self.text.split('\n')
        self.line = Line(Salitix_Client_Number=self.Salitix_Client_Number(),
                            Salitix_Customer_Number=self.Salitix_Customer_Number(),
                            SAL_Invoice_type=self.SAL_Invoice_type(self.lines),
                            Unit_Funding_Type=self.Unit_Funding_Type(self.lines),
                            Line_Description=self.Line_Description(self.lines),
                            Deal_Type=self.Deal_Type(self.lines),
                            Invoice_No=self.Invoice_No(filename),
                            Invoice_Date=self.Invoice_Date(self.lines),
                            Promotion_No=self.Promotion_No(self.lines),
                            Product_No=self.Product_No(self.lines),
                            Week=self.Week(self.lines),
                            Period=self.Period(self.lines),
                            Year=self.Year(self.lines),
                            Start_Date=self.Start_Date(self.lines),
                            End_Date=self.End_Date(self.lines),
                            Quantity=float(self.Quantity(self.lines)) if self.Quantity(self.lines) != 'N/A' and self.Quantity(self.lines) != ''  else self.Quantity(self.lines),
                            Unit_Price = str(float(self.Net_Amount(self.lines))/float(self.Quantity(self.lines))) if self.Unit_Price(self.lines) == '' and self.Quantity(self.lines) !='' else self.Unit_Price(self.lines),
                            Net_Amount=self.Net_Amount(self.lines),
                            VAT_Amount=self.VAT_Amount(self.lines),
                            Gross_Amount= self.Gross_Amount(self.lines) if float(self.Gross_Amount(self.lines)) == float(self.VAT_Amount(self.lines))+float(self.Net_Amount(self.lines)) else str(float(self.VAT_Amount(self.lines))+float(self.Net_Amount(self.lines))),
                            Store_Format=self.Store_Format(self.lines),
                            Invoice_Description=self.Invoice_Description(self.lines),
                            Acquisition_Ind=self.Acquisition_Ind(self.lines))                      


    def Salitix_Client_Number(self):
        return 'CL002'

    def Salitix_Customer_Number(self):
        return 'COO01'
    
    def SAL_Invoice_type(self,lines):
        PR_list=['Trading Income Invoice']
        if self.Deal_Type(lines) in PR_list:
            return 'PR'
        elif self.Deal_Type(lines) == 'N/A':
            return 'N/A'
        elif self.Deal_Type(lines) == 'Credit':
            return 'PR'
        elif self.Deal_Type(lines) == 'Miscellaneous':
            return 'MS'

    def Unit_Funding_Type(self,lines):
        if self.SAL_Invoice_type(lines) == 'PR':
            return 'E'
        elif self.SAL_Invoice_type(lines) == 'N/A':
            return 'N/A'
        else:
            return ''
    
    def Line_Description(self,lines):
        index_list=[]
        store='N'
        for index,line in enumerate(lines):
            if "Code VAT Value Total" in line:
                store='Y'
                continue
            elif "Turnover or Number of Units" in line:
                store='N'
            if store=='Y':
                index_list.append(index)
            elif store=='N':
                None
        Line_Description_list=[lines[x] for x in index_list]
        Line_Description='\n'.join(Line_Description_list)
        Line_Description=Line_Description.replace('\n',' ')
        if re.search(r'^(.*) ([0-9.]*) ([|]) ([0-9.]*) ([0-9.]*) ([0-9.]*) (.*)$',Line_Description):
            Line_Description=re.search(r'^(.*) ([0-9.]*) ([|]) ([0-9.]*) ([0-9.]*) ([0-9.]*) (.*)$',Line_Description).group(1)+re.search(r'^(.*) ([0-9.]*) ([|]) ([0-9.]*) ([0-9.]*) ([0-9.]*) (.*)$',Line_Description).group(7)
            return Line_Description
        elif Line_Description=='':
            return 'N/A'
        else:
            return Line_Description
    
    def Deal_Type(self,lines):
        if "TC" in self.filename:
            return 'Credit'
        elif "VI" in self.filename:
            return "Miscellaneous"
        for line in lines:
            if re.search(r'Invoice Type: ([A-Za-z]*)',line):
                return re.search(r'Invoice Type: ([A-Za-z]*)',line).group(1)
            elif 'Trading Income Invoice' in line:
                return 'Trading Income Invoice'
        return 'N/A'
    
    #COOP Invoices should already be named correctly.
    def Invoice_No(self,filename):
        Invoice_No_filename = filename.replace('.tif','')
        Invoice_No_filename = Invoice_No_filename.replace('.pdf','')
        Invoice_No_filename_list = Invoice_No_filename.split('\\')
        Invoice_No = Invoice_No_filename_list[-1]
        return Invoice_No

    def Invoice_Date(self,lines):
        for line in lines:
            if re.search(r'Invoice Date ([0-9]{2}\/[0-9]{2}\/[0-9]{4})',line):
                return re.search(r'Invoice Date ([0-9]{2}\/[0-9]{2}\/[0-9]{4})',line).group(1)
            elif "VI" in self.filename:
                if re.search(r'^([0-9]{2}\/[0-9]{2}\/[0-9]{4})$',line):
                    return re.search(r'^([0-9]{2}\/[0-9]{2}\/[0-9]{4})$',line).group(1)
        return 'N/A'
    
    def Promotion_No(self,lines):
        for line in lines:
            if re.search(r'Deal Number ([0-9]*)',line):
                return re.search(r'Deal Number ([0-9]*)',line).group(1)
        return 'Couldn\'t find Promotion No.'
    
    def Product_No(self,lines):
        return 'Manual'
    
    def Week(self,lines):
        try:
            if re.search(r'WK ([0-9]) ',self.Line_Description(lines)):
                return re.search(r'WK ([0-9]) ',self.Line_Description(lines)).group(1)
        except:return 'N/A'
    
    def Period(self,lines):
        for line in lines:
            if re.search(r'Period ([0-9]*)',line):
                return re.search(r'Period ([0-9]*)',line).group(1)
        try:
            if re.search(r'P(\d+) 20[12][0-9]',self.Line_Description(lines)):
                return re.search(r'P(\d+) 20[12][0-9]',self.Line_Description(lines)).group(1)
        except:return 'N/A'
        return 'N/A'
    
    def Year(self,lines):
        for line in lines:
            if re.search(r'Year ([0-9]*)',line):  
                    return re.search(r'Year ([0-9]*)',line).group(1).replace('5','2')
        try:
            if re.search(r'P(\d+) (20[12][0-9])',self.Line_Description(lines)):
                return re.search(r'P(\d+) (20[12][0-9])',self.Line_Description(lines)).group(2).replace('5','2')
        except:None
        return 'N/A'
    
    def Start_Date(self,lines):
        if self.Deal_Type(lines)=='Trading Income Invoice':
            try:
                year_df=Calendar_df[Calendar_df['Year']==int(self.Year(lines))]
                period_df=year_df[year_df['Period']==int(self.Period(lines))]
                week_df=period_df[period_df['Week']==int(self.Week(lines))]
                return week_df['Start_Date'].values[0]
            except:return 'N/A'
        else:
            try:
                year_df=Calendar_df[Calendar_df['Year']==int(self.Year(lines))]
                period_df=year_df[year_df['Period']==int(self.Period(lines))]
                list=week_df['Start_Date']
                return list[0]
            except:return 'N/A'
            

    def End_Date(self,lines):
        if self.Deal_Type(lines)=='Trading Income Invoice':
            try:
                year_df=Calendar_df[Calendar_df['Year']==int(self.Year(lines))]
                period_df=year_df[year_df['Period']==int(self.Period(lines))]
                week_df=period_df[period_df['Week']==int(self.Week(lines))]
                return week_df['End_Date'].values[0]
            except:return 'N/A'
        else:
            try:
                year_df=Calendar_df[Calendar_df['Year']==int(self.Year(lines))]
                period_df=year_df[year_df['Period']==int(self.Period(lines))]
                list=week_df['End_Date']
                return list[-1]
            except:return 'N/A'

    def Quantity(self,lines):
        for line in lines:
            if re.search(r'Turnover or Number of Units(\s?)([]|_ ]*?) ([0-9.,]*)',line):
                if re.search(r'Turnover or Number of Units(\s?)([]|_ ]*?) _([0-9,.]*)',line):
                    if re.search(r'Turnover or Number of Units(\s?)([]|_ ]*?) ([0-9.,]*) ',line):
                        return re.search(r'Turnover or Number of Units(\s?)([]|_ ]*?) ([0-9,.]*) ',line).group(3).replace(',','')
                    return re.search(r'Turnover or Number of Units(\s?)([]|_ ]*?) _([0-9,.]*)',line).group(3).replace(',','')
                elif re.search(r'Turnover or Number of Units(\s?)([]|_]*)([0-9.,]*)',line):
                    if re.search(r'Turnover or Number of Units(\s?)([]|_]*)([0-9.,]*)',line).group(3).replace(',','') != '':
                        return re.search(r'Turnover or Number of Units(\s?)([]|_]*)([0-9.,]*)',line).group(3).replace(',','')
                    else:
                        None
                if re.search(r'Turnover or Number of Units(\s?)([]|_ ]*?) ([0-9,.]*)',line).group(3).replace(',','') != '':
                    return re.search(r'Turnover or Number of Units(\s?)([]|_ ]*?) ([0-9,.]*)',line).group(3).replace(',','')
                else: None
            if re.search(r'Turnover or Number of Units(\s?)([]|_ ]*?) _([0-9.,]*)',line):
                return re.search(r'Turnover or Number of Units(\s?)([]|_ ]*?) _([0-9,.]*)',line).group(3).replace(',','')
            if re.search(r'Turnover or Number of Units(\s?)([]|_ ]*?) ([0-9.,]*) ',line):
                return re.search(r'Turnover or Number of Units(\s?)([]|_ ]*?) ([0-9,.]*) ',line).group(3).replace(',','')
            if re.search(r'Turnover or Number of Units(\s?)([]|_]*)([0-9.,]*)',line):
                return re.search(r'Turnover or Number of Units(\s?)([]|_]*)([0-9.,]*)',line).group(3).replace(',','')
        try:
            return float(self.Net_Value(lines))/float(self.Unit_Price(lines))
        except:return 'N/A'
    
    def Unit_Price(self,lines):
        for line in lines:
            if re.search(r'Rate per Unit or %([]| _]*?) ([0-9.]*)',line):
                if re.search(r'Rate per Unit or %([]| _]*?) [_-]([0-9.]*)',line):
                    return re.search(r'Rate per Unit or %([]| _]*?) [_-]([0-9.]*)',line).group(2)
                return re.search(r'Rate per Unit or %([]| _]*?) ([0-9.]*)',line).group(2)
            elif re.search(r'Rate per Unit or %([]| _]*?) [_-]([0-9.]*)',line):
                return re.search(r'Rate per Unit or %([]| _]*?) [_-]([0-9.]*)',line).group(2)
            elif re.search(r'Rate per Unit or %([]| _]*?) ([0-9.]*)%',line):
                percent = re.search(r'Rate per Unit or %([]| _]*?) ([0-9.]*)%',line).group(2)
                return float(percent)/100
            elif re.search(r'Rate per Unit or %([]| _]*?)[.]([0-9.]*)%',line):
                percent = re.search(r'Rate per Unit or %([]| _]*?)[.]([0-9.]*)%',line).group(2)
                return float(percent)/100
            elif re.search(r'Rate per Unit or %([]|_-—]*)([0-9]*).([0-9]*)',line):
                    return re.search(r'Rate per Unit or %([]|_-—]*)([0-9.]*).([0-9]*)',line).group(2) + re.search(r'Rate per Unit or %([]|_-—]*)([0-9.]*).([0-9]*)',line).group(3)
        return 'N/A'
    
    def Net_Amount(self,lines):
        for line in lines:
            if re.search(r'Invoice Totals ([0-9.]*) ([0-9.]*) ([0-9.]*)',line):
                return re.search(r'Invoice Totals ([0-9.]*) ([0-9.]*) ([0-9.]*)',line).group(1)
        return 'N/A'
    
    def VAT_Amount(self,lines):
        for line in lines:
            if re.search(r'Invoice Totals ([0-9.]*) ([0-9.]*) ([0-9.]*)',line):
                return re.search(r'Invoice Totals ([0-9.]*) ([0-9.]*) ([0-9.]*)',line).group(2)
        return 'N/A'
    
    def Gross_Amount(self,lines):
        for line in lines:
            if re.search(r'Invoice Totals ([0-9.]*) ([0-9.]*) ([0-9.]*)',line):
                if float(self.Net_Amount(lines)) + float(self.VAT_Amount(lines)) != float(re.search(r'Invoice Totals ([0-9.]*) ([0-9.]*) ([0-9.]*)',line).group(3)):
                    return re.search(r'Invoice Totals ([0-9.]*) ([0-9.]*) ([0-9.]*)',line).group(3).replace('3','8')
                return re.search(r'Invoice Totals ([0-9.]*) ([0-9.]*) ([0-9.]*)',line).group(3)
        return 'N/A'
    
    def Store_Format(self,lines):
        for line in lines:
            if re.search(r'Buying Category ([A-Za-z]*)',line):
                return re.search(r'Buying Category ([A-Za-z]*)',line).group(1)
        return 'N/A'
    
    def Invoice_Description(self,lines):
        try:
            if "TCG" in self.Line_Description(lines):
                return "TCG"
            elif "FRTS" in self.Line_Description(lines):
                return "FRTS"
            else:
                return "N/A"
        except:return "N/A"
    
    def Acquisition_Ind(self,lines):
        return 'A'

def FRTS_VS_TCG(df,base_path):
    vsline=[]
    Promotion_No_list=df['Promotion_No'].tolist()
    Already_Done=[]
    for i in Promotion_No_list:
        if i not in Already_Done:
            try:
                promo_df=df[df['Promotion_No']==i]
                TCG_sum=float(promo_df[promo_df['Invoice_Description']=='TCG']['Quantity'].sum())
                FRTS_sum=float(promo_df[promo_df['Invoice_Description']=='FRTS']['Quantity'].sum())
                FRTS_percentage=FRTS_sum/(TCG_sum+FRTS_sum)
                Invoice_Count=len(promo_df)
                vsline.append(TCGLine(i,TCG_sum,FRTS_sum,FRTS_percentage,Invoice_Count))
                Already_Done.append(i)
            except:None
    vsdf=pd.DataFrame(vsline)
    vsdf.to_excel(base_path+'//'+'COOP_FRTS.xlsx',index=False)



run_through_files(r'W:\Audit\Pladis\Invoice Images\EmailStagingBay\CoOp')


#string='[Turnover or Number of Units |_021147.0 | Rate per Unit or %| 000.31'
#print(re.search(r'Turnover or Number of Units(\s?)([]|_ ]*?) _([0-9,.]*)',string).group(3).replace(',',''))
