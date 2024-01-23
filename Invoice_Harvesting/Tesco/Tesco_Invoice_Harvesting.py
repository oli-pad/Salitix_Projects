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
                os.rename(os.path.join(path,filename),os.path.join(r"C:\Users\Python\Desktop\Tesco test\Incomplete",filename.replace("_1","")))
                continue
            except:
                os.replace(os.path.join(path,filename),os.path.join(r"C:\Users\Python\Desktop\Tesco test\Incomplete",filename.replace("_1","")))
                continue

file_renaming(r"C:\Users\Python\Desktop\Tesco test\Unsplit Files")
