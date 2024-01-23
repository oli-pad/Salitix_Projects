#Below for regular expression analysis
import re
#Below is what reads the pdf page by page and stores it as a variable
import pdfplumber
import os
import shutil

#Checking the text and outputting the deal types.
def Defining_Retailer(file):
    Tesco_re=re.compile(r'KETTLE FOODS')
    pdf_text=''
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            pdf_text+=text
    for line in pdf_text.split('\n'):
        line = " ".join(line.split())
        tesco=Tesco_re.search(line)
        if tesco:
            return "Tesco"
    return False
image_folder=r'C:\Users\python\Desktop\Tesco test\Incomplete'
folder=r'C:\Users\python\Desktop\Tesco test\Complete'
image_folder_list=[item for item in os.listdir(image_folder) if ".pdf" in item]
for i in image_folder_list:
    try:
        Retailer=Defining_Retailer(os.path.join(image_folder,i))
        if Retailer==False:
            continue
        else:
            shutil.copy(os.path.join(image_folder,i),os.path.join(folder,i))
    except:None
