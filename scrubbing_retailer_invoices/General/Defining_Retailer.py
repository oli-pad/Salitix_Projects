#Below for regular expression analysis
import re
#Below is what reads the pdf page by page and stores it as a variable
import pdfplumber

#Checking the text and outputting the deal types.
def Defining_Retailer(file):
    Tesco_re=re.compile(r'Tesco')
    Morrisons_re=re.compile(r'Morrison')
    ASDA_re=re.compile(r'ASDA')
    Sainsbury_Re=re.compile(r'Sainsbury')
    pdf_text=''
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            pdf_text+=text
    for line in pdf_text.split('\n'):
        line = " ".join(line.split())
        tesco=Tesco_re.search(line)
        morrisons=Morrisons_re.search(line)
        asda=ASDA_re.search(line)
        sainsbury=Sainsbury_Re.search(line)
        if tesco:
            return "Tesco"
        if morrisons:
            return "Morrisons"
        if asda:
            return "Asda"
        if sainsbury:
            return "Sainsburys"
    return False 
    
def Invoice_infomation(file,retailer):
    TES_Invoice_No_re=re.compile(r'Invoice(.*)No(.*):(.*)')
    ASD_Invoice_No_re=re.compile(r'Invoice(.*)Number: (\d+)')
    MOR_Invoice_No_re=re.compile(r'Document Number: (.*)$')
    SAI_Invoice_No_re=re.compile(r'Invoice Number[:;] (.*)')
    pdf_text=''
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            pdf_text+=text
    for line in pdf_text.split('\n'):
        line = " ".join(line.split())
        TES_Inv=TES_Invoice_No_re.search(line)
        ASD_Inv=ASD_Invoice_No_re.search(line)
        MOR_Inv=MOR_Invoice_No_re.search(line)
        SAI_Inv=SAI_Invoice_No_re.search(line)
        if TES_Inv and retailer=='Tesco':
            Invoice_No=TES_Inv.group(3)
            Invoice_No=Invoice_No.replace(" ","")
            return Invoice_No
        if ASD_Inv and retailer=='Asda':
            Invoice_No=ASD_Inv.group(2)
            Invoice_No=Invoice_No.replace(" ","")
            return Invoice_No
        if MOR_Inv and retailer=='Morrisons':
            Invoice_No=MOR_Inv.group(1)
            split_out=Invoice_No.split("-")
            Invoice_No=split_out[-1]
            Invoice_No=Invoice_No.replace("_","")
            return Invoice_No
        if SAI_Inv and retailer=='Sainsburys':
            Invoice_No=SAI_Inv.group(1)
            Invoice_No=Invoice_No.replace("/","_")
            Invoice_No=Invoice_No.replace("/","_")
            return Invoice_No
    return False