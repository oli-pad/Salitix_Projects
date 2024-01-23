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

#Input from calling the file and the parameters as such.
script,Client_Name,User_Email,User_Password,number_of_days=argv

def get_log_in_details(Client_Name,User_Email,User_Password):
    #log_ins=pd.read_csv(file)
    time.sleep(5)
    Get_data(Client_Name,User_Email,User_Password)
    time.sleep(5)
    logoff()
    time.sleep(5)

def Get_data(client_name,username,password):
    selecting_dates,selecting_downloads=dates_for_download(int(number_of_days))
    login(Tesco_toolkit,username,password)
    for i in selecting_dates:
        setup_epos(EPOS_URL)
        choose_date(i[0],i[1],i[2],i[3])

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

def setup_epos(url):
    time.sleep(5)
    driver.get(url)
    WebDriverWait(driver,150).until(EC.presence_of_element_located((By.ID, "tpnb_sales_store_format")))
    driver.find_element(By.ID,"tpnb_sales_store").click()
    time.sleep(1)
    driver.find_element(By.ID,"selectedDate").click()

def choose_date(dd,mm,yyyy,day):
    WebDriverWait(driver,150).until(EC.presence_of_element_located((By.XPATH,"//button[@class='styled__BaseButton-sc-3mnirm-0 styled__PrimaryButton-sc-3mnirm-2 hfJtwr gwfuNO beans-button__container']")))
    time.sleep(5)
    driver.find_element(By.XPATH,"//button[@class='styled__BaseButton-sc-3mnirm-0 styled__SecondaryButton-sc-3mnirm-3 dXycGT cqClUN beans-date-picker__calendar-button beans-button__container']").click()
    try:
        l= driver.find_element(By.XPATH,"//td[@aria-label='Selected date: "+dd+" "+mm+", "+yyyy+", "+day+"']")
        s= l.text
        driver.find_element(By.XPATH,"//td[@aria-label='Selected date: "+dd+" "+mm+", "+yyyy+", "+day+"']").click()
    except:
        driver.find_element(By.XPATH,"//button[@aria-label='Previous month']").click()
        time.sleep(5)
        driver.find_element(By.XPATH,"//td[@aria-label='Selected date: "+dd+" "+mm+", "+yyyy+", "+day+"']").click()
    time.sleep(3)
    WebDriverWait(driver,150).until(EC.presence_of_element_located((By.XPATH,"//button[@class='styled__BaseButton-sc-3mnirm-0 styled__PrimaryButton-sc-3mnirm-2 hfJtwr gwfuNO beans-button__container']")))
    driver.find_element(By.XPATH,"//button[@class='styled__BaseButton-sc-3mnirm-0 styled__PrimaryButton-sc-3mnirm-2 hfJtwr gwfuNO beans-button__container']").click()
    time.sleep(1)

def logoff():
    driver.find_element(By.ID,"profile").click()
    time.sleep(2)
    driver.find_element(By.ID,"signout").click()
    time.sleep(2)

#get_log_in_details(r'C:\Users\Oliver.Oakes\OneDrive - Salitix\Desktop\projects\web_portal_scraping\docs\Tesco_log_ins.csv')

get_log_in_details(Client_Name,User_Email,User_Password)

driver.quit()
