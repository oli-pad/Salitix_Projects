import os
import pandas as pd

def make_folder(folder_path,client):
    if not os.path.exists(folder_path.format(client)):
        os.makedirs(folder_path.format(client))

def get_client(file):
    df = pd.read_excel(file)
    client=str(df["Vendor Name"].loc[1])
    return client

def main():
    Store_folder_path = r"C:\Users\python\Desktop\ASDA EXCEL FILES\{}"

    Excel_folder_path = r"C:\Users\python\Desktop\ASDA EXCEL FILES"
    Excel_files= [item for item in os.listdir(Excel_folder_path) if item.endswith('.xlsx')]

    for i in Excel_files:
        print(i)
        client=get_client(os.path.join(Excel_folder_path,i))
        make_folder(Store_folder_path,client)
        try:
            os.rename(os.path.join(Excel_folder_path,i),os.path.join(Store_folder_path.format(client),i))
        except:
            os.remove(os.path.join(Excel_folder_path,i))
            continue