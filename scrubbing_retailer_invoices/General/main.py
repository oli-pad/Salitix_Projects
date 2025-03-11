#This file will feed from the flask form

# Path: scrubbing_retailer_invoices/General/main.py

import os
from sys import argv

script,process,client,retailer,start_date,end_date=argv

print("Process: ",process," Client: ",client," Retailer: ",retailer)

#Harvesting
Harvesting_format=r"python C:\Users\python\Desktop\projects\Invoice_Harvesting\General\Harvesting.py {} {}"
#Rename
Rename_format=r"python C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\General\Rename_Invoices.py {}"
#Copy
Copy_format=r"python C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\General\Copy_Retailer_Invoices.py {}"
#Scrubbing
Scrubbing_format=r'python C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\General\Scrubbing_all_Invoices.py "{}" "{}"'
#Scraping
Scraping_format=r"python C:\Users\python\Desktop\projects\web_portal_scraping\ASDA_Retail_Link\Repeating_Code.py {} {}"
#Loading
Loading_format=r"python C:\Users\python\Desktop\projects\Excel_Customer_Charges\ASDA_Excel_Customer_Charges.py {}"
#Transfer
Transfer_format=r"python C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\General\Run_Format_Procedure.py"
#Run the Identify Client Number
Identify_Client_format=r"python C:\Users\python\Desktop\IdentifyingInvoiceClientNumber\main.py"
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
    print("All Process")
    os.system(Harvesting_format.format(client[0],retailer))
    print("Harvesting Done")
    os.system(Rename_format.format(client[0]))
    print("Renaming Done")
    os.system(Copy_format.format(client[0]))
    print("Copying Done")
    os.system(Scrubbing_format.format(client[0],retailer_list))
    print("Scrubbing Done")
    if "ASDA" in retailer_list:
        print("ASDA Scraping")
        os.system(Scraping_format)
        print("ASDA Scraping Done")
        os.system(Loading_format.format(client[0]))
        print("ASDA Loading Done")
    os.system(Transfer_format)
    print("Transfer Done")
    os.system(Identify_Client_format)
    print("All Process Done")
    print("Checking for any incorrect images")
    print("Running Second Stage Scrubbing")
    for i in retailer_list:
        os.system(Update_Header_format.format(client[0],i))
    print("Header Done")
    for retailer in retailer_list:
        os.system(Load_into_format.format(client[0],retailer))
    print("Load into IA Procedure Done")
    print("All Process Done")
elif process == "Harvest":
    print("Harvesting")
    os.system(Harvesting_format.format(client[0],retailer))
    print("Harvesting Done")
elif process == "Rename":
    print("Renaming")
    os.system(Rename_format.format(client[0]))
    print("Renaming Done")
elif process == "Copy":
    print("Copying")
    os.system(Copy_format.format(client[0]))
    print("Copying Done")
elif process == "Scrub":
    print("Scrubbing")
    print(Scrubbing_format.format(client[0],retailer_list))
    os.system(Scrubbing_format.format(client[0],retailer_list))
    print("Scrubbing Done")
elif process == "ASDA only : Scraping":
    print("ASDA Scraping")
    os.system(Scraping_format.format(start_date,end_date))
    print("ASDA Scraping Done")
elif process == "ASDA only : Load":
    print("ASDA Loading")
    os.system(Loading_format.format(client[0]))
    print("ASDA Loading Done")
elif process == "Transfer to Ftd table":
    print("Transfering")
    # os.system(Transfer_format)
    print("Transfer Done")
    print("Identifying Client Number")
    os.system(Identify_Client_format)
    print("ALL Done")
else:
    print("Invalid Process Contact OO for help.")
