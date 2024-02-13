import requests
import pandas as pd
import re
import time
from datetime import date
from datetime import timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from pathlib import Path
import shutil
from collections import namedtuple
from sys import argv
from openpyxl import load_workbook
from openpyxl import Workbook
import csv

driver = webdriver.Chrome(executable_path=r'J:\Code\web_portal_scraping\Teco_Toolkit_Daily_EPOS\chromedriver.exe')
days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
months={'01':"January","02":"February","03":"March","04":"April","05":"May","06":"June","07":"July","08":"August","09":"September","10":"October","11":"November","12":"Decemeber"}
short_months={"January":"Jan","February":"Feb","March":"Mar","April":"Apr","May":"May","June":"Jun","July":"Jul","August":"Aug","September":"Sep","October":"Oct","November":"Nov","Decemeber":"Dec"}
folder_name={"BACARDI":"Bacardi","AB_INBEV":"Ab_Inbev","AG_BARR":"AG_Barr","BURTONS":"Burtons","COTY":"Coty","FINSBURY_FOODS":"Finsbury_Foods",
"HEINEKEN":"Heineken","KETTLE_FOODS":"Kettle_foods","KINNERTON":"Kinnerton","KP_SNACKS":"KP_Snacks","MAXXIUM":"Maxxium","PLADIS":"Pladis",
"PREMIER_FOODS":"Premier_foods","TILDA":"Tilda","WEETABIX":"Weetabix","YOUNGS":"Youngs","PRINCES":"Princes","LOREAL":"Loreal"}
###Log in page####       
Tesco_toolkit=r'https://partnerstoolkit.tesco.com/sign-in/?url=%2Ftoolkit%2F'
EPOS_URL=r'https://partnerstoolkit.tesco.com/partner/reports/'

Line = namedtuple('Line',"Client_Name File_Name Status")
report=[]
lines=[]

script,Client_Name,User_Email,User_Password,number_of_days,start_num=argv

def get_download_data(Client_Name,User_Email,User_Password):
    time.sleep(5)
    download_data(Client_Name,User_Email,User_Password)
    time.sleep(5)
    logoff()

def download_data(client_name,username,password):
    selecting_dates,selecting_downloads=dates_for_download(int(number_of_days))
    login(Tesco_toolkit,username,password)
    time.sleep(5)
    print(selecting_downloads)
    download_files(selecting_downloads)
    #CSV_to_Excels()
    rename_relocate(client_name)

def dates_for_download(n):
    date_list=[]
    download_list=[]
    today = date.today()-timedelta(int(start_num))
    for i in range(n):
        Dates=today-timedelta(1+i)
        date_one = Dates.strftime("%d/%m/%Y")
        day=Dates.weekday()
        if date_one[0] == "0":
            date_list.append([date_one[1],months[date_one[3:5]],date_one[6:],days[day]])
        else:
            date_list.append([date_one[:2],months[date_one[3:5]],date_one[6:],days[day]])
    for j in date_list:
        download_list.append('Tesco-Sales_and_stock-TPNB_Sales_x_store-'+str(j[2])+short_months[j[1]]+str(j[0])+".xlsx")
    return date_list,download_list

def login(url,username,password):
   driver.get(url)
   time.sleep(1)
   WebDriverWait(driver,150).until(EC.presence_of_element_located((By.ID,"partner-signin-btn")))
   driver.find_element(By.ID,"partner-signin-btn").click()
   time.sleep(1)
   WebDriverWait(driver,150).until(EC.presence_of_element_located((By.ID,"email-address")))
   driver.find_element(By.ID,"email-address").send_keys(username)
   driver.find_element(By.ID,"Password").send_keys(password)
   time.sleep(1)
   driver.find_element(By.XPATH,"//button[@class='styled__StyledBaseButton-sc-1nxj3l4-0 gLwaFm ddsweb-button styled__StyledTextButton-sc-8hxn3m-0 caIwqa styled__StyledButton-cwlXRi fDqbBn ddsweb-button--text-button']").click()

def download_files(selecting_downloads):
    time.sleep(20)
    driver.get("https://partnerstoolkit.tesco.com/partner/reports/stored")
    WebDriverWait(driver,150).until(EC.presence_of_element_located((By.ID,"downloadedReports")))
    driver.find_element(By.ID,'downloadedReports').click()
    time.sleep(200)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    links=soup.find_all("a")
    selecting_downloads=[i.replace(".xlsx",".csv") for i in selecting_downloads]
    for i in links:
        if i.text in selecting_downloads:
            time.sleep(60)
            driver.find_element(By.ID,i.get('id')).click()

def CSV_to_Excels():
    time.sleep(40)
    selecting_dates,selecting_downloads=dates_for_download(int(number_of_days))
    selecting_downloads=[i.replace(".xlsx",".csv") for i in selecting_downloads]
    for i in selecting_downloads:
        try:
            df=pd.read_csv(os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),i),sep=None)
            df.to_excel(os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),i.replace(".csv",".xlsx")),sheet_name='Store Level LDI',index=False)
            os.remove(os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),i))
        except:None

def rename_relocate(client_name):
    time.sleep(30)
    selecting_dates,selecting_downloads=dates_for_download(int(number_of_days))
    rename_path="Z:\{}\EPOS Store\Tesco\Daily"
    file_list=dir_contents(rename_path.format(folder_name[client_name]))
    if client_name == "MAXXIUM":
        for i in selecting_downloads:
            wb=load_workbook(os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),i))
            ws=wb['Store Level LDI'].values
            columns = next(ws)[0:]
            df = pd.DataFrame(ws,columns=columns)
            to_drop=[]
            for j in df.index:
                if df.loc[j].at["Supplier"]==36308 or df.loc[j].at["Supplier"]==59365:
                    to_drop.append(j)
            df=df.drop(to_drop)
            df.to_csv(os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),i),sheet_name='Store Level LDI',index=False)
    elif client_name == "KETTLE_FOODS":
        for i in selecting_downloads:
            wb=load_workbook(os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),i))
            ws=wb['Store Level LDI'].values
            columns = next(ws)[0:]
            df = pd.DataFrame(ws,columns=columns)
            to_drop=[]
            for j in df.index:
                if df.loc[j].at["Supplier"]==61814 or df.loc[j].at["Supplier"]==59365:
                    to_drop.append(j)
            df=df.drop(to_drop)
            df.to_csv(os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),i),sheet_name='Store Level LDI',index=False)
    else:None
    selecting_downloads=[i.replace(".xlsx",".csv") for i in selecting_downloads]
    for i in selecting_downloads:
        #try:
        name=i.replace(".csv"," {}.csv".format(folder_name[client_name]))
        if name not in file_list:
            os.rename(os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),i),os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),name))
            shutil.move(os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),name),os.path.join(rename_path.format(folder_name[client_name]),name))
        else:
            os.rename(os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),i),os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),name))
            os.replace(os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),name),os.path.join(rename_path.format(folder_name[client_name]),name))
        #except:None

def dir_contents(path):
    file_list=[]
    for root, directories, files in os.walk(path):
        for filename in files:
            file_list.append(files)
    return file_list

def logoff():
    time.sleep(30)
    driver.find_element(By.ID,"profile").click()
    time.sleep(2)
    driver.find_element(By.ID,"signout").click()
    time.sleep(2)

get_download_data(Client_Name,User_Email,User_Password)
driver.quit()
