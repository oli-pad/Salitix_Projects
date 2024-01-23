import os
from Defining_Retailer import Defining_Retailer
from Defining_Retailer import Invoice_infomation
import shutil

#List of things in the Audit folder.
directory_list = [ item for item in os.listdir(r"W:\Audit")]

invoice_image_folder_path="W:\Audit\{}\Invoice Images"
invoice_image_path="W:\Audit\{}\Invoice Images\{}"

#Folders to be used for process.
audit_folder_list=[item for item in directory_list if os.path.exists(invoice_image_folder_path.format(item))]

#User input
print(audit_folder_list)
Client=str(input("Please select a client from above or type 'all'   >   "))
while Client!="all" and Client not in audit_folder_list:
    Client=str(input("Please select a client from above or type 'all'   >   "))
   
if Client=='all':
    audit_folder_list.remove('Export com')
    client_list=audit_folder_list
else:
    client_list=[Client]

for client in client_list:
    image_folder=invoice_image_folder_path.format(client)
    image_folder_list=[item for item in os.listdir(image_folder) if ".pdf" in item or ".PDF" in item]
    for i in image_folder_list:
        print(i)
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
