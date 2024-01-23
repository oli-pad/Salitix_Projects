from PyPDF2 import PdfWriter, PdfReader, PdfMerger
import os
import re
import pdfplumber

def file_splitter(base_path):
    for filename in listdir_nohidden(base_path):
        print(filename)
        input_pdf = PdfReader(os.path.join(base_path,filename))
        for i in range(len(input_pdf.pages)):
            output = PdfWriter()
            output.add_page(input_pdf.pages[i])
            with open(r"C:\Users\Python\Desktop\test\Split Files\File"+str(i)+filename, "wb") as output_stream:
                output.write(output_stream)

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

filenames=[]
Invoice_Nos=[]
def define_pdfs(base_path):
    for filename in listdir_nohidden(base_path):
        text=Read_pdf(os.path.join(base_path,filename))
        Invoice_No=Invoice_Number(text)
        Invoice_No=Invoice_No.replace("/","_")
        Invoice_No=Invoice_No.replace("/","_")
        filenames.append(filename)
        Invoice_Nos.append(Invoice_No)


Invoice_No_re=re.compile(r'Invoice Number[:;] (.*)')
def Invoice_Number(text):
    for line in text.split('\n'):
        line = " ".join(line.split())
        invoice=Invoice_No_re.search(line)
        if invoice:
            Invoice_No=invoice.group(1)
            Invoice_No=Invoice_No.replace("/","_")
            Invoice_No=Invoice_No.replace("/","_")
            return Invoice_No
    return "T&C"

def Read_pdf(file):
    pdf_text=''
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            pdf_text+=text
    return pdf_text

merged=[]
def unique_files(base_path,filenames,Invoice_Nos):
    for i in range(len(filenames)):
        if filenames in merged:continue
        else:
            output = PdfMerger()
            index_of_invoice=[j for j,val in enumerate(Invoice_Nos) if val==Invoice_Nos[i]]
            act_filename=filenames[i]
            act_filename=act_filename.partition("_")[2]
            for y in index_of_invoice:
                if act_filename not in filenames[y]:
                    index_of_invoice.remove(y)
            for x in index_of_invoice:
                output.append(os.path.join(base_path,filenames[x]))
                merged.append(filenames[x])
            if Invoice_Nos[i]=="T&C":continue
            with open(r"C:\Users\Python\Desktop\test\Incomplete\\"+Invoice_Nos[i].replace("\\","")+".pdf", "wb") as output_stream:
                output.write(output_stream)

file_splitter(r"C:\Users\Python\Desktop\test\Unsplit Files")
define_pdfs(r"C:\Users\Python\Desktop\test\Split Files")
unique_files(r"C:\Users\Python\Desktop\test\Split Files",filenames,Invoice_Nos)
2
