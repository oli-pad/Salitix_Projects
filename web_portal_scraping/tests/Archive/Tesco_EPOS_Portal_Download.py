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
import pyautogui
import os
from pathlib import Path
import shutil
from collections import namedtuple
from sys import argv

options = webdriver.ChromeOptions()
options.add_argument("download.default_directory=C:/Documents, download.prompt_for_download=False")
driver = webdriver.Chrome(options=options)
days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
months={'01':"January","02":"February","03":"March","04":"April","05":"May","06":"June","07":"July","08":"August","09":"September","10":"October","11":"November","12":"Decemeber"}
short_months={"January":"Jan","February":"Feb","March":"Mar","April":"Apr","May":"May","June":"Jun","July":"Jul","August":"Aug","September":"Sep","October":"Oct","November":"Nov","Decemeber":"Dec"}
folder_name={"BACARDI":"Bacardi","AB_Inbev":"Ab_Inbev","AG_BARR":"AG_Barr","BURTONS":"Burtons","COTY":"Coty","FINSBURY_FOODS":"Finsbury_Foods",
"HEINEKEN":"Heineken","KETTLE_FOODS":"Kettle_foods","KINNERTON":"Kinnerton","KP_SNACKS":"KP_Snacks","MAXXIUM":"Maxxium","PLADIS":"Pladis",
"PREMIER_FOODS":"Premier_foods","TILDA":"Tilda","WEETABIX":"Weetabix","YOUNGS":"Youngs"}
###Log in page####
Tesco_toolkit=r'https://partnerstoolkit.tesco.com/sign-in/?url=%2Ftoolkit%2F'
EPOS_URL=r'https://partnerstoolkit.tesco.com/partner/reports/'

Line = namedtuple('Line',"Client_Name File_Name Status")
report=[]
lines=[]

script,Client_Name,User_Email,User_Password,number_of_days=argv

def get_download_data(Client_Name,User_Email,User_Password):
    time.sleep(5)
    download_data(Client_Name,User_Email,User_Password)
    time.sleep(5)
    logoff()

def download_data(client_name,username,password):
    selecting_dates,selecting_downloads=dates_for_download(int(number_of_days))
    login(Tesco_toolkit,username,password)
    time.sleep(2)
    download_files(selecting_downloads)
    rename_relocate(client_name)

def dates_for_download(n):
    date_list=[]
    download_list=[]
    today = date.today()-timedelta(3)
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
   driver.find_element(By.XPATH,"//button[@class='styled__BaseButton-sc-3mnirm-0 styled__PrimaryButton-sc-3mnirm-2 eNmss kEYaXJ styled__StyledButton-cwlXRi fDqbBn beans-button__container']").click()

def download_files(selecting_downloads):
    time.sleep(20)
    driver.get("https://partnerstoolkit.tesco.com/partner/reports/stored")
    WebDriverWait(driver,150).until(EC.presence_of_element_located((By.XPATH,"//button[@class='styled__BaseButton-sc-3mnirm-0 styled__SecondaryButton-sc-3mnirm-3 cDaVlJ gOEhxG styled__StyledButton-sc-1d68kik-1 ijThGB beans-actions-menu__button beans-button__container']")))
    soup = BeautifulSoup(driver.page_source,"html.parser")
    links=soup.find_all("a")
    for i in links:
        if i.text in selecting_downloads:
            time.sleep(20)
            driver.find_element(By.ID,i.get('id')).click()

def rename_relocate(client_name):
    time.sleep(30)
    selecting_dates,selecting_downloads=dates_for_download(int(number_of_days))
    rename_path="Z:\{}\EPOS Store\Tesco\Daily"
    file_list=dir_contents(rename_path.format(folder_name[client_name]))
    if client_name == "MAXXIUM":
        for i in selecting_downloads:
            df = pd.read_excel(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),i))
            to_drop=[]
            for j in df.index:
                if df.loc[j].at["Supplier"]==36308:
                    to_drop.append(j)
            df=df.drop(to_drop)
            df.to_excel(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),i),sheet_name='Store Level LDI',index=False)
    elif client_name == "KETTLE_FOODS":
        for i in selecting_downloads:
            df = pd.read_excel(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),i))
            to_drop=[]
            for j in df.index:
                if df.loc[j].at["Supplier"]==61814:
                    to_drop.append(j)
            df=df.drop(to_drop)
            df.to_excel(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),i),sheet_name='Store Level LDI',index=False)
    else:None
    for i in selecting_downloads:
        name=i.replace(".xlsx"," {}.xlsx".format(folder_name[client_name]))
        if name not in file_list:
            try:
                os.rename(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),i),os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),name))
                shutil.move(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),name),os.path.join(rename_path.format(folder_name[client_name]),name))
                report.append(Line(client_name,name,"Downloaded"))
            except:
                report.append(Line(client_name,name,"Failed"))
                continue
        else:
            try:
                os.rename(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),i),os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),name))
                os.replace(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),name),os.path.join(rename_path.format(folder_name[client_name]),name))
                report.append(Line(client_name,name,"Downloaded"))
            except:
                report.append(Line(client_name,name,"Failed"))
                continue

def exceptions_report(lines):
    df=pd.DataFrame(lines)
    df.to_csv('Exception_Reports/exceptions {}.csv'.format(date.today().strftime("%d_%m_%Y")),index=False)

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
#exceptions_report(lines)
driver.quit()
