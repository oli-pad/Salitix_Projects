import os
from sys import argv
import shutil

script, Client = argv

Invoice_Image_Folder_path_2="W:\Audit\{}\Invoice Images\{}"
Invoice_Image_Folder_path="W:\Audit\{}\Invoice Images\EmailStagingBay"
Email_Staging_path="W:\Audit\{}\Invoice Images\EmailStagingBay\{}"
Email_Staging_path_2="W:\Audit\{}\Invoice Images\EmailStagingBay\{}\{}"

Retailer_List = [item for item in os.listdir(Invoice_Image_Folder_path.format(Client)) if os.path.isdir(os.path.join(Invoice_Image_Folder_path.format(Client), item))]

#Script to check a folder to see if files exist
#if files exist remove them
# if they don't run a script

print("Running Invoice Harvesting Script for {}".format(Client))

for Retailer in Retailer_List:
    if Retailer == "Asda":
        #ASDA just go straight into the invoice image folder
        #move all files from the email staging bay to the invoice image folder
        for file in os.listdir(Email_Staging_path.format(Client, Retailer)):
            if file == "Thumbs.db":
                pass
            elif file == "desktop.ini":
                pass
            elif file == "":
                pass
            if ".PDF" in file or ".pdf" in file:
                #if file exists remove else move
                if os.path.isfile(Invoice_Image_Folder_path_2.format(Client,file)):
                    os.remove(Email_Staging_path_2.format(Client, Retailer, file))
                else:
                    shutil.move(Email_Staging_path_2.format(Client, Retailer, file), Invoice_Image_Folder_path_2.format(Client,file))
            
    elif Retailer == "Tesco":
        #TESCO just go straight into the invoice image folder
        #move all files from the email staging bay to the invoice image folder
        for file in os.listdir(Email_Staging_path.format(Client, Retailer)):
            if file == "Thumbs.db":
                pass
            elif file == "desktop.ini":
                pass
            elif file == "":
                pass
            if ".PDF" in file or ".pdf" in file:
            #if file exists remove else move
                if os.path.isfile(Invoice_Image_Folder_path_2.format(Client,file)):
                    os.remove(Email_Staging_path_2.format(Client, Retailer, file))
                else:
                    shutil.move(Email_Staging_path_2.format(Client, Retailer, file), Invoice_Image_Folder_path_2.format(Client,file))
    elif Retailer == "Sainsburys":
        #Sainsburys get taken to a sub folder
        #Processed by being split then renamed
        #move all files from the email staging bay to a local folder
        #First check folders to make sure they are empty
        if len(os.listdir(r"C:\Users\python\Desktop\test\Unsplit Files")) != 0:
            for file in os.listdir(r"C:\Users\python\Desktop\test\Unsplit Files"):
                os.remove(r"C:\Users\python\Desktop\test\Unsplit Files\{}".format(file))
        if len(os.listdir(r"C:\Users\python\Desktop\test\Split Files")) != 0:
            for file in os.listdir(r"C:\Users\python\Desktop\test\Split Files"):
                os.remove(r"C:\Users\python\Desktop\test\Split Files\{}".format(file))
        if len(os.listdir(r"C:\Users\python\Desktop\test\Incomplete")) != 0:
            for file in os.listdir(r"C:\Users\python\Desktop\test\Incomplete"):
                if os.path.isfile(Invoice_Image_Folder_path_2.format(Client,file)):
                    os.remove(r"C:\Users\python\Desktop\test\Incomplete\{}".format(file))
                else:    
                    shutil.move(r"C:\Users\python\Desktop\test\Incomplete\{}".format(file), Invoice_Image_Folder_path_2.format(Client,file))     
        if len(os.listdir(r"C:\Users\python\Desktop\test\Complete")) != 0:
            for file in os.listdir(r"C:\Users\python\Desktop\test\Complete"):
                #if file exists remove else move
                if os.path.isfile(Invoice_Image_Folder_path_2.format(Client,file)):
                    os.remove(r"C:\Users\python\Desktop\test\Complete\{}".format(file))
                else:    
                    shutil.move(r"C:\Users\python\Desktop\test\Complete\{}".format(file), Invoice_Image_Folder_path_2.format(Client,file))
        for file in os.listdir(Email_Staging_path.format(Client, Retailer)):
            if file == "Thumbs.db":
                pass
            elif file == "desktop.ini":
                pass
            elif file == "":
                pass
            if ".PDF" in file or ".pdf" in file:
                if os.path.isfile(Invoice_Image_Folder_path_2.format(Client,file)):
                    os.remove(Email_Staging_path_2.format(Client, Retailer, file))
                else:
                    shutil.move(Email_Staging_path_2.format(Client, Retailer, file), r"C:\Users\python\Desktop\test\Unsplit Files\{}".format(file))
        #run the split script
        os.system(r"python C:\Users\python\Desktop\projects\Invoice_Harvesting\Sainsbury\Sainsbury_Invoice_Harvesting.py")
        #move all files from the complete folder to the invoice image folder
        for file in os.listdir(r"C:\Users\python\Desktop\test\Incomplete"):
            #if file exists remove else move
            if os.path.isfile(Invoice_Image_Folder_path_2.format(Client,file)):
                os.remove(r"C:\Users\python\Desktop\test\Incomplete\{}".format(file))
            else:
                shutil.move(r"C:\Users\python\Desktop\test\Incomplete\{}".format(file), Invoice_Image_Folder_path_2.format(Client,file))
    elif Retailer == "Morrisons":
        #Morrisons get taken to a sub folder
        #Processed by being split then renamed
        #move all files from the email staging bay to a local folder
        #First check folders to make sure they are empty
        if len(os.listdir(r"C:\Users\python\Desktop\Morrisons test\Unsplit Files")) != 0:
            for file in os.listdir(r"C:\Users\python\Desktop\Morrisons test\Unsplit Files"):
                os.remove(r"C:\Users\python\Desktop\Morrisons test\Unsplit Files\{}".format(file))
        if len(os.listdir(r"C:\Users\python\Desktop\Morrisons test\Split Files")) != 0:
            for file in os.listdir(r"C:\Users\python\Desktop\Morrisons test\Split Files"):
                os.remove(r"C:\Users\python\Desktop\Morrisons test\Split Files\{}".format(file))
        if len(os.listdir(r"C:\Users\python\Desktop\Morrisons test\Incomplete")) != 0:
            for file in os.listdir(r"C:\Users\python\Desktop\Morrisons test\Incomplete"):
                if os.path.isfile(Invoice_Image_Folder_path_2.format(Client,file)):
                    os.remove(r"C:\Users\python\Desktop\Morrisons test\Incomplete\{}".format(file))
                else:
                    shutil.move(r"C:\Users\python\Desktop\Morrisons test\Incomplete\{}".format(file), Invoice_Image_Folder_path_2.format(Client,file))        
        if len(os.listdir(r"C:\Users\python\Desktop\Morrisons test\Complete")) != 0:
            for file in os.listdir(r"C:\Users\python\Desktop\Morrisons test\Complete"):
                if os.path.isfile(Invoice_Image_Folder_path_2.format(Client,file)):
                    os.remove(r"C:\Users\python\Desktop\Morrisons test\Complete\{}".format(file))
                else:
                    shutil.move(r"C:\Users\python\Desktop\Morrisons test\Complete\{}".format(file), Invoice_Image_Folder_path_2.format(Client,file))
        for file in os.listdir(Email_Staging_path.format(Client, Retailer)):
            if file == "Thumbs.db":
                pass
            elif file == "desktop.ini":
                pass
            elif file == "":
                pass
            if ".PDF" in file or ".pdf" in file:
                if os.path.isfile(Invoice_Image_Folder_path_2.format(Client,file)):
                    os.remove(Email_Staging_path_2.format(Client, Retailer, file))
                else:
                    shutil.move(Email_Staging_path_2.format(Client, Retailer, file), r"C:\Users\python\Desktop\Morrisons test\Unsplit Files\{}".format(file))
        #run the split script
        os.system(r"python C:\Users\python\Desktop\projects\Invoice_Harvesting\Morrisons\Morrisons_Invoice_Harvesting.py")
        #move all files from the complete folder to the invoice image folder
        for file in os.listdir(r"C:\Users\python\Desktop\Morrisons test\Incomplete"):
            if os.path.isfile(Invoice_Image_Folder_path_2.format(Client,file)):
                os.remove(r"C:\Users\python\Desktop\Morrisons test\Incomplete\{}".format(file))
            else:
                shutil.move(r"C:\Users\python\Desktop\Morrisons test\Incomplete\{}".format(file), Invoice_Image_Folder_path_2.format(Client,file))

print("Script Complete")


