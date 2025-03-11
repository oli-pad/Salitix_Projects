#This file will feed from the flask form

# Path: scrubbing_retailer_invoices/General/main.py

import os
from sys import argv

script,process,client,retailer=argv

print("Process: ",process," Client: ",client," Retailer: ",retailer)

#Update_Header
Update_Header_format=r"python C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\Updating_Hdr\Updating_Hdr_of_Ftd.py {} {}"
#Load into
Load_into_format=r"python C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\General\IA_Procedure.py {} {}"

client=[client]
if retailer == "All":
    retailer_list=["ASDA","Sainsburys","Tesco","Morrisons"]
else:
    retailer_list=[retailer]


if process == "All":
    for i in retailer_list:
        os.system(Update_Header_format.format(client[0],i))
    print("Transfer Done")
    for retailer in retailer_list:
        os.system(Load_into_format.format(client[0],retailer))
    print("Load into IA Procedure Done")
    print("All Process Done")
elif process == "Update HDR Column":
    print("Update HDR Column")
    for i in retailer_list:
        os.system(Update_Header_format.format(client[0],i))
    print("Update Header Done")
elif process == "Load into IA Procedure":
    print("Load into IA Procedure")
    for retailer in retailer_list:
        os.system(Load_into_format.format(client[0],retailer))
    print("Load into IA Procedure Done")
else:
    print("Invalid Process Contact OO for help.")
