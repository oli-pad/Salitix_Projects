from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import os
import re
import pdfplumber



def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f


def file_renaming(path):
    for filename in listdir_nohidden(path):
        if "[" in filename:
            continue
        else:
            try:
                if "ASDA Invoice #" in filename:
                    os.rename(os.path.join(path,filename),os.path.join(r"C:\Users\Python\Desktop\ASDA Images\Incomplete",filename.replace("ASDA Invoice #","")))
                    continue
                elif "ASDA Credit Note #" in filename:
                    os.rename(os.path.join(path,filename),os.path.join(r"C:\Users\Python\Desktop\ASDA Images\Incomplete",filename.replace("ASDA Credit Note #","")))
                    continue
            except:
                if "ASDA Invoice #" in filename:
                    os.replace(os.path.join(path,filename),os.path.join(r"C:\Users\Python\Desktop\ASDA Images\Incomplete",filename.replace("ASDA Invoice #","")))
                    continue
                elif "ASDA Credit Note #" in filename:
                    os.replace(os.path.join(path,filename),os.path.join(r"C:\Users\Python\Desktop\ASDA Images\Incomplete",filename.replace("ASDA Credit Note #","")))
                    continue

file_renaming(r"C:\Users\Python\Desktop\ASDA Images\Unsplit Files")
