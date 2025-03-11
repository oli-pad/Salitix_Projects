import os
from Defining_Retailer import Defining_Retailer
import shutil

from sys import argv

script,Client=argv

#List of things in the Audit folder.
directory_list = [ item for item in os.listdir(r"W:\Audit")]

invoice_image_folder_path="W:\Audit\{}\Invoice Images"
invoice_image_path="W:\Audit\{}\Invoice Images\{}"

#Folders to be used for process.
audit_folder_list=[item for item in directory_list if os.path.exists(invoice_image_folder_path.format(item))]

if Client=='manual':
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
    image_folder_list=[item for item in os.listdir(image_folder) if ".pdf" in item]
    for i in image_folder_list:
        try:
            Retailer=Defining_Retailer(invoice_image_path.format(client,i))
            if Retailer==False:
                continue
            else:
                shutil.copy(invoice_image_path.format(client,i), invoice_image_path.format(client,"ImageStagingBay"+"\\"+Retailer+"\\"+i))
        except:None
    print(client+" is complete.")
