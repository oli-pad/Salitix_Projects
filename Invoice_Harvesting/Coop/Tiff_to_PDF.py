import pytesseract
from PIL import Image
import os
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Python\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

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

Invoice_No_re=re.compile(r'Invoice No T[I1lLi](.*)$')
backup_Invoice_No_re=re.compile(r'T[I1lLi]([0-9O]*)$')
secondary_backup_Invoice_No_re=re.compile(r'T[I1lLi]([0-9O]*) ([0-9O]*)$')
tertiary_backup_Invoice_No_re=re.compile(r'7[I1lLi]([0-9O]{8})$')
def get_invoice_number(text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        invoice=Invoice_No_re.search(line)
        invoice2=backup_Invoice_No_re.search(line)
        invoice3=secondary_backup_Invoice_No_re.search(line)
        invoice4=tertiary_backup_Invoice_No_re.search(line)
        if invoice:
            second_part=invoice.group(1)
            second_part=second_part.replace("O","0")
            second_part=second_part.replace(" ","")
            #if len(second_part)>=8:second_part=second_part.replace("0","")
            Invoice_No="TI"+second_part
            print(Invoice_No,"     ",second_part)
            return Invoice_No
        elif invoice2:
            second_part=invoice2.group(1)
            second_part=second_part.replace("O","0")
            second_part=second_part.replace(" ","")
            #if len(second_part)>=8:second_part=second_part.replace("0","")
            Invoice_No="TI"+second_part[:9]
            print(Invoice_No,"     ",second_part)
            return Invoice_No
        elif invoice3:
            second_part=invoice3.group(1)+invoice3.group(2)
            second_part=second_part.replace("O","0")
            second_part=second_part.replace(" ","")
            #if len(second_part)>=8:second_part=second_part.replace("0","")
            Invoice_No="TI"+second_part[:9]
            print(Invoice_No,"     ",second_part)
            return Invoice_No
        elif invoice4:
            second_part=invoice4.group(1)
            second_part=second_part.replace("O","0")
            second_part=second_part.replace(" ","")
            Invoice_No="TI"+second_part[:9]
            print(Invoice_No,"     ",second_part)
            return Invoice_No
    return False

Statement_re=re.compile(r'STATEMENT')
Statement_Date_re=re.compile(r'Statement Date (.*)')
Backup_Statement_Date_re=re.compile(r'(\d{2})-(.*)-(\d{2})')
def get_statement_number(text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        statment_date=Statement_Date_re.search(line)
        Backup_Statement_Date=Backup_Statement_Date_re.search(line)
        if statment_date:
            date=statment_date.group(1)
            return date
        elif Backup_Statement_Date:
            date=Backup_Statement_Date.group(1)+"-"+Backup_Statement_Date.group(2)+"-"+Backup_Statement_Date.group(3)
            return date
    return False

Credit_No_re=re.compile(r'Invoice No T[C](.*)$')
backup_Credit_No_re=re.compile(r'T[Cc]([0-9O]*)$')
secondary_backup_Credit_No_re=re.compile(r'T[C]([0-9O]*) ([0-9O]*)$')
def get_credit_number(text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        invoice=Credit_No_re.search(line)
        invoice2=backup_Credit_No_re.search(line)
        invoice3=secondary_backup_Credit_No_re.search(line)
        if invoice:
            second_part=invoice.group(1)
            second_part=second_part.replace("O","0")
            second_part=second_part.replace(" ","")
            if len(second_part)>8:second_part=second_part[1:9]
            Invoice_No="TC"+second_part
            print(Invoice_No,"     ",second_part)
            return Invoice_No
        elif invoice2:
            second_part=invoice2.group(1)
            second_part=second_part.replace("O","0")
            second_part=second_part.replace(" ","")
            if len(second_part)>8:second_part=second_part[1:9]
            Invoice_No="TC"+second_part[:9]
            print(Invoice_No,"     ",second_part)
            return Invoice_No
        elif invoice3:
            second_part=invoice3.group(1)+invoice3.group(2)
            second_part=second_part.replace("O","0")
            second_part=second_part.replace(" ","")
            if len(second_part)>8:second_part=second_part[1:9]
            Invoice_No="TC"+second_part[:9]
            print(Invoice_No,"     ",second_part)
            return Invoice_No
    return False

Misc_No_re=re.compile(r'Invoice No [Vv][I1lLi](.*)$')
backup_Misc_No_re=re.compile(r'V[I1lLi]*([0-9O]*)$')
secondary_backup_Misc_No_re=re.compile(r'V[I1lLi]([0-9O]*) ([0-9O]*)$')
def get_misc_number(text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        invoice=Misc_No_re.search(line)
        invoice2=backup_Misc_No_re.search(line)
        invoice3=secondary_backup_Misc_No_re.search(line)
        if invoice:
            second_part=invoice.group(1)
            second_part=second_part.replace("O","0")
            second_part=second_part.replace(" ","")
            second_part=second_part.replace("l","")
            Invoice_No="VI"+second_part
            print(Invoice_No,"     ",second_part)
            return Invoice_No
        elif invoice2:
            second_part=invoice2.group(1)
            second_part=second_part.replace("O","0")
            second_part=second_part.replace(" ","")
            second_part=second_part.replace("l","")
            Invoice_No="VI"+second_part[:8]
            print(Invoice_No,"     ",second_part)
            return Invoice_No
        elif invoice3:
            second_part=invoice3.group(1)+invoice3.group(2)
            second_part=second_part.replace("O","0")
            second_part=second_part.replace(" ","")
            second_part=second_part.replace("l","")
            Invoice_No="VI"+second_part[:8]
            print(Invoice_No,"     ",second_part)
            return Invoice_No
    print(text)
    return False

missing_letter_re=re.compile(r'Invoice No [I1lLi](.*)$')
coupon_re=re.compile('[cC]oupon')
def no_leading_letter(text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        Invoice_No=missing_letter_re.search(line)
        status=False
        if Invoice_No:
            status=True
            break
    if status:
        for line in text.split('\n'):
            coupon=coupon_re.search(line)
            if coupon:
                print("VI"+Invoice_No.group(1))
                return "VI"+Invoice_No.group(1)
        print("TI"+Invoice_No.group(1))
        return "TI"+Invoice_No.group(1)
    return False



base_path=r"W:\Audit\Pladis\Invoice Images\EmailStagingBay\CoOp\to split\oli"

def rename_coop_invoices(base_path):
    for filename in listdir_nohidden(base_path):
        if ".tif" in filename:
            text=tiff_to_txt(os.path.join(base_path,filename))
        elif ".pdf" in filename or ".PDF" in filename:
            text=Read_pdf(os.path.join(base_path,filename))
        if get_statement_number(text):
            date=get_statement_number(text)
            try:
                os.rename(os.path.join(base_path,filename),os.path.join(base_path,"Statement "+date+".tif"))
            except:
                os.replace(os.path.join(base_path,filename),os.path.join(base_path,"Statement "+date+".tif"))
        elif get_invoice_number(text):
            Invoice_No=get_invoice_number(text)
            try:
                os.rename(os.path.join(base_path,filename),os.path.join(base_path,Invoice_No+".tif"))
            except:None
        elif get_credit_number(text):
            Invoice_No=get_credit_number(text)
            try:
                os.rename(os.path.join(base_path,filename),os.path.join(base_path,Invoice_No+".tif"))
            except:None
        elif get_misc_number(text):
            Invoice_No=get_misc_number(text)
            try:
                os.rename(os.path.join(base_path,filename),os.path.join(base_path,Invoice_No+".tif"))
            except:None
        elif no_leading_letter(text):
            Invoice_No=no_leading_letter(text)
            try:
                os.rename(os.path.join(base_path,filename),os.path.join(base_path,Invoice_No+".tif"))
            except:None
        else:
            print(filename)
        #else:continue

rename_coop_invoices(base_path)