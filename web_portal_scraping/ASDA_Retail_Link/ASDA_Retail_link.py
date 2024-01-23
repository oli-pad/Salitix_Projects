import requests
import pandas as pd
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
import getpass

options = webdriver.ChromeOptions()
options.add_argument("download.default_directory=C:/Documents, download.prompt_for_download=False")
driver = webdriver.Chrome(options=options)

#email=input("Please input e-mail >")
email,password='',''
#password=getpass.getpass("Please input password >")
#data={'Username':[email],'Password':[password]}
#df=pd.DataFrame(data)
#df.to_csv("Oli_Oakes_Holiday_2021.csv")

ASDA_Charges=pd.read_csv(r'C:\Users\Python\Desktop\ASDA Images\Scrubbed_Charges\ASDA_Charges.csv')

Retail_link_url=r"https://retaillink.login.wal-mart.com"
Retail_link_apps_url=r'https://wmsupplierportal.wal-mart.com/irj/portal?ukey=w5790'

def login(url, username, password):
   driver.get(url)
   time.sleep(5)
   #input("Ready to log on? >")
   driver.find_element(By.XPATH,"//input[@data-automation-id='uname']").send_keys(username)
   time.sleep(2)
   driver.find_element(By.XPATH,"//input[@data-automation-id='pwd']").send_keys(password)
   #soup=BeautifulSoup(driver.page_source,"html.parser")
   #email=soup.find(attrs={'data-automation-id':'uname'})['value']
   #password=soup.find(attrs={'data-automation-id':'pwd'})['value']
   #data2={'Username':[email],'Password':[password]}
   #df2=pd.DataFrame(data2)
   #df2.to_csv("Oli_Oakes_Holiday_2020.csv")
   time.sleep(5)
   driver.find_element(By.XPATH,"//button[@data-automation-id='loginBtn']").click()
   #input("Ready to download files? >")
   time.sleep(5)

def supplier_portal(url):
    driver.get(url)
    WebDriverWait(driver,150).until(EC.presence_of_element_located((By.ID,"ARROWL2N3")))
    driver.find_element(By.ID,"ARROWL2N3").click()
    time.sleep(5)
    driver.find_element(By.XPATH,"//span[text()='Transaction Report']").click()
    time.sleep(5)

def download_excel(agreement,start_date,end_date):
    time.sleep(10)
    driver.switch_to.default_content()
    frame = driver.find_element(By.ID,"contentAreaFrame")
    driver.switch_to.frame(frame)
    frame = driver.find_element(By.ID,"isolatedWorkArea")
    driver.switch_to.frame(frame)
    try:
        driver.find_element(By.ID,"WDCD").clear()
        driver.find_element(By.ID,"WDCD").send_keys(str(agreement))
    except:
        driver.find_element(By.ID,"WDCD").clear()
        driver.find_element(By.ID,"WDCD").send_keys(str(agreement))
    time.sleep(5)
    driver.find_element(By.ID,"WD0122").click()
    time.sleep(10)
    try:
        driver.find_element(By.ID,"WD0257").click()
        time.sleep(10)
        # driver.switch_to.default_content()
        frame = driver.find_element(By.ID,"URLSPW-0")
        driver.switch_to.frame(frame)
        soup=BeautifulSoup(driver.page_source,"html.parser")
        input=soup.find_all(class_="urEdf2TxtEnbl lsEdfLeftBrdRadius lsEdf3TxtHlpBtn urBorderBox")
        driver.find_element(By.ID,input[0].get('id')).send_keys(start_date[:2]+"."+start_date[3:5]+"."+start_date[6:])
        time.sleep(2)
        # driver.find_element(By.ID,"WD02F9").send_keys(start_date[:2]+"."+start_date[3:5]+"."+start_date[6:])
        # time.sleep(2)
        driver.find_element(By.ID,input[1].get('id')).send_keys(end_date[:2]+"."+end_date[3:5]+"."+end_date[6:])
        time.sleep(2)
        driver.find_element(By.XPATH,"//a[@title='OK ']").click()
        time.sleep(10)
    except:
        None
    driver.switch_to.default_content()
    frame = driver.find_element(By.ID,"contentAreaFrame")
    driver.switch_to.frame(frame)
    frame = driver.find_element(By.ID,"isolatedWorkArea")
    driver.switch_to.frame(frame)
    driver.find_element(By.ID,"WD01CD").click()
    time.sleep(10)
    driver.find_element(By.ID,"WD01CD-MnuIco").click()
    time.sleep(3)
    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    time.sleep(1)
    actions.send_keys(Keys.ARROW_DOWN)
    actions.perform()
    actions.send_keys(Keys.ENTER)
    actions.perform()
    print("Enter")
    time.sleep(10)
    #pyautogui.press("enter")
    #pyautogui.press("enter")

def rename_file(inv_no):
    time.sleep(40)
    try:
        os.rename(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),"export.xlsx"),os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),inv_no+".xlsx"))
        os.rename(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),inv_no+".xlsx"),os.path.join(r"C:\Users\python\Desktop\ASDA EXCEL FILES",inv_no+".xlsx"))
    except:
        time.sleep(30)
        os.rename(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),"export.xlsx"),os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),inv_no+".xlsx"))
        os.rename(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),inv_no+".xlsx"),os.path.join(r"C:\Users\python\Desktop\ASDA EXCEL FILES",inv_no+".xlsx"))
    time.sleep(5)

def dir_contents(path):
    file_list=[]
    for root, directories, files in os.walk(path):
        for filename in files:
            for i in files:
                file_list.append(i)
    return file_list

def Full_Download(df,downloaded_list):
    login(Retail_link_url,"Roland@tilda.com","Tildarice16")
    time.sleep(60)
    supplier_portal(Retail_link_apps_url)
    for i in df.index:
        print(df["Invoice_No"].loc[i])
        if str(df["Invoice_No"].loc[i])+".xlsx" in downloaded_list:
            continue
        elif df["Promotion_No"].loc[i]=="NAN" or df["Promotion_No"].loc[i]==None or df["Promotion_No"].loc[i]=="" or str(df["Promotion_No"].loc[i])=="nan" or str(df["Deal_Type"].loc[i])=="Fixed Agreement":
            continue
        else:
            #try:
            download_excel(df["Promotion_No"].loc[i],str(df["Start_Date"].loc[i]),str(df["End_Date"].loc[i]))
            rename_file(str(df["Invoice_No"].loc[i]))
            # except:
            #     df.drop([i],inplace = True)
            #     df.to_csv(r'C:\Users\Python\Desktop\ASDA Images\Scrubbed_Charges\ASDA_Charges.csv',index=False)
            #     driver.close()
            #     break


downloaded_list=dir_contents(r"C:\Users\python\Desktop\ASDA EXCEL FILES")
Full_Download(ASDA_Charges,downloaded_list)
