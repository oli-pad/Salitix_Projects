import os
from Defining_Retailer import Defining_Retailer
from Defining_Retailer import Invoice_infomation
import shutil
import subprocess

from sys import argv


script,Client=argv
#List of things in the Audit folder.
directory_list = [ item for item in os.listdir(r"W:\Audit")]

invoice_image_folder_path="W:\Audit\{}\Invoice Images"
invoice_image_path="W:\Audit\{}\Invoice Images\{}"

#Folders to be used for process.
audit_folder_list=[item for item in directory_list if os.path.exists(invoice_image_folder_path.format(item))]

#User input
if Client=='manual':
    print(audit_folder_list)
    Client=str(input("Please select a client from above or type 'all'   >   "))
    while Client!="all" and Client not in audit_folder_list:
        Client=str(input("Please select a client from above or type 'all'   >   "))
    
if Client=='All':
    audit_folder_list.remove('Export com')
    print('ALL')
    client_list=audit_folder_list
else:
    client_list=[Client]

for client in client_list:
    image_folder=invoice_image_folder_path.format(client)
    image_folder_list=[item for item in os.listdir(image_folder) if ".pdf" in item or ".PDF" in item]
    for i in image_folder_list:
        print('I:', i)
        print('Client:', Client)
        print(invoice_image_path.format(client, i))
        Retailer=Defining_Retailer(invoice_image_path.format(client,i))
        if Retailer==False:
            continue
        else:
            Invoice_No=Invoice_infomation(invoice_image_path.format(client,i),Retailer)
            if Invoice_No:
                print(str(invoice_image_path.format(client,Invoice_No)))
                print("+"+str(invoice_image_path.format(client,i)))
                if invoice_image_path.format(client,i)==invoice_image_path.format(client,Invoice_No+".pdf"):
                    continue
                elif os.path.exists(invoice_image_path.format(client,Invoice_No+".pdf")):
                    if invoice_image_path.format(client,i)!=invoice_image_path.format(client,Invoice_No+".pdf"):
                        os.remove(invoice_image_path.format(client,i))
                else:
                    os.rename(invoice_image_path.format(client,i),invoice_image_path.format(client,Invoice_No+".pdf"))
      #  except:None
    print(client+" is complete.")

# 05/06 JR temporarily put repairing PDFs in the rename script. ONLY FOR BURTONS. Commented out so this routine runs rename process as normal.
# When running below function, comment out above function so only one runs at a time.
'''def repair_pdf(input_path, output_path):
    # path to the folder containing the corrupted PDFs
    corrupted_folder="W:\Audit\Burtons\Invoice Images\CorruptedPDFs"
    # list of corrupted PDFs in the corrupted folder
    corrupted_folder_list=[item for item in os.listdir(corrupted_folder) if ".pdf" in item or ".PDF" in item]
    # loop through the list of corrupted PDFs and repair them
    for i in corrupted_folder_list:
        try:
            # File path to ghostscript executable
            ghostscript_executable = r"C:\Program Files\gs\gs10.03.1\bin\gswin64c.exe"
            subprocess.run([ghostscript_executable, "-o", output_path.format(i), "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/prepress", input_path.format(i)], check=True)
            # prints the path of the repaired PDF
            print(f"Repaired PDF saved as {output_path.format(i)}")
        except subprocess.CalledProcessError as e:
            # prints the error message
            print(f"An error occurred: {e}")
        except FileNotFoundError:
            # prints the error message for not finding the ghostscript executable
            print("Ghostscript executable not found. Ensure the path is correct.")

# input path for corrupted PDFs. {} is a placeholder for the file name (i)
input_path = "W:\Audit\Burtons\Invoice Images\CorruptedPDFs\{}"
# output path for repaired PDFs. {} is a placeholder for the file name (i)
output_path = "W:\Audit\Burtons\Invoice Images\RepairedPDFs\{}"
# call the function to repair the PDFs
repair_pdf(input_path, output_path)'''
