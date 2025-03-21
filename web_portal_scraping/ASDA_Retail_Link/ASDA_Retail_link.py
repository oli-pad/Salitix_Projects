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
import pyodbc
import sys
import string

script, username, password = sys.argv

options = webdriver.ChromeOptions()
options.add_argument("download.default_directory=C:/Documents, download.prompt_for_download=False")
driver = webdriver.Chrome(options=options)


ASDA_Charges=pd.read_csv(r'C:\Users\Python\Desktop\ASDA Images\Scrubbed_Charges\ASDA_Charges.csv')

Retail_link_url=r"https://retaillink.login.wal-mart.com"
Retail_link_apps_url=r'https://wmsupplierportal.wal-mart.com/irj/portal?ukey=w5790'

def login(url, username, password):
   driver.get(url)
   time.sleep(5)
   driver.find_element(By.XPATH,"//input[@data-automation-id='uname']").send_keys(username)
   time.sleep(2)
   driver.find_element(By.XPATH,"//input[@data-automation-id='pwd']").send_keys(password)
   time.sleep(60)
   #New MFA script below...
   driver.find_element(By.XPATH,"//button[@data-automation-id='loginBtn']").click()
   print("MFA")
   time.sleep(10)
   driver.find_element(By.XPATH,"//button[@data-automation-id='card-button']").click()
   time.sleep(30)
   mfaDataFrame = pd.read_csv(r"J:\Text Message Log.csv")
   mfaDataFrame = mfaDataFrame[mfaDataFrame["Sent Number"] == "SYMVIPWMT"]
   print(mfaDataFrame)
   mfaCode = mfaDataFrame["Code"].iloc[-1]
   mfaCode=mfaCode[-7:-1]
   print(mfaCode)
   driver.find_element(By.XPATH,"//input[@data-automation-id='code']").send_keys(mfaCode)
   time.sleep(2)
   driver.find_element(By.XPATH,"//button[@dataautomationid='card-button']").click()
   time.sleep(50)

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
    # Fill out the agreement number
    print(agreement)
    try:
        driver.find_element(By.ID,"WDCD").clear()
        driver.find_element(By.ID,"WDCD").send_keys(str(agreement))
    except:
        driver.find_element(By.ID,"WDCD").clear()
        driver.find_element(By.ID,"WDCD").send_keys(str(agreement))
    time.sleep(5)
    # Search button
    driver.find_element(By.ID,"WD0122").click()
    time.sleep(10)
    try:
        print(start_date,end_date)
        # Click on the agreement amount
        driver.find_element(By.ID,"WD0257").click()
        time.sleep(10)
        # driver.switch_to.default_content()
        frame = driver.find_element(By.ID,"URLSPW-0")
        driver.switch_to.frame(frame)
        soup=BeautifulSoup(driver.page_source,"html.parser")
        input=soup.find_all(class_="urEdf2TxtEnbl lsEdfLeftBrdRadius lsEdf3TxtHlpBtn urBorderBox")
        driver.find_element(By.ID,input[0].get('id')).send_keys(start_date[0:2]+"."+start_date[3:5]+"."+start_date[6:10]) # 20/03 JR changed date character locations to type
        time.sleep(2)
        # driver.find_element(By.ID,"WD02F9").send_keys(start_date[:2]+"."+start_date[3:5]+"."+start_date[6:])
        # time.sleep(2)
        driver.find_element(By.ID,input[1].get('id')).send_keys(end_date[0:2]+"."+end_date[3:5]+"."+end_date[6:10]) # 20/03 JR changed date character locations to type
        time.sleep(2)
        driver.find_element(By.XPATH,"//a[@title='OK ']").click()
        time.sleep(30)
        # Finish inputting the dates
    except Exception as e:
        print(f"Failed with {agreement}: {e}")
    driver.switch_to.default_content()
    frame = driver.find_element(By.ID,"contentAreaFrame")
    driver.switch_to.frame(frame)
    frame = driver.find_element(By.ID,"isolatedWorkArea")
    driver.switch_to.frame(frame)
    # CLick on the Item Number
    time.sleep(5)
    #  <span id="WD01EF" ct="CP" lsdata="{1:'Item\x20Number',4:false}" class="">Item Number</span>
    driver.find_element(By.XPATH,"//span[text()='Item Number']").click()
    time.sleep(2)
    # WD01F1-cnt get the height of this element
    driver.find_element(By.ID,"WD01F1-cnt")
    style = driver.find_element(By.ID, "WD01F1-cnt").get_attribute("style")
    # time.sleep(500)
    try:
        height = re.search(r'height:\s*(\d+)px', style).group(1)
        print(f"Height of the element is: {height}px")
        x = int(height) / 22
        x = x - 6
    except:
        aria_setsize = driver.find_element(By.ID,"WD01F1").get_attribute("aria-setsize")
        x = int(aria_setsize) - 5
    for i in range(1,int(x)+1):
        actions = ActionChains(driver)
        actions.send_keys(Keys.ARROW_DOWN)
        actions.perform()
        time.sleep(2)
        actions.send_keys(Keys.ARROW_DOWN)
        actions.perform()
        time.sleep(2)
        actions.send_keys(Keys.ARROW_DOWN)
        actions.perform()
        time.sleep(2)
        actions.send_keys(Keys.ARROW_DOWN)
        actions.perform()
        time.sleep(2)
        actions.send_keys(Keys.ARROW_DOWN)
        actions.perform()
        time.sleep(2)
        for j in range(i):
            actions.send_keys(Keys.ARROW_DOWN)
            actions.perform()
            time.sleep(2)
        actions.send_keys(Keys.ENTER)
        actions.perform()
        time.sleep(2)
        driver.find_element(By.ID,"WD01CD").click()
        time.sleep(10)
        driver.find_element(By.ID,"WD01CD-MnuIco").click()
        time.sleep(3)
        actions.send_keys(Keys.ENTER)
        actions.perform()
        time.sleep(1)
        actions.send_keys(Keys.ARROW_DOWN)
        actions.perform()
        actions.send_keys(Keys.ENTER)
        actions.perform()
        print("Enter")
        time.sleep(10)
        driver.find_element(By.XPATH,"//span[text()='Item Number']").click()
        time.sleep(2)
    #Get the tables from the files and append them to eachother then save into the export file
    df = pd.read_excel(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),"export.xlsx"))
    # remove the export file to avoid confusion
    os.remove(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),"export.xlsx"))
    try:
        for i in range(1,int(x)):
            df1 = pd.read_excel(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),f"export ({i}).xlsx"))
            os.remove(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),f"export ({i}).xlsx"))
            df = pd.concat([df,df1])
    except Exception as e:
        print(e)
        None
    df.to_excel(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),"export.xlsx"),index=False)       


def rename_file(inv_no):
    # OO to change
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
    login(Retail_link_url, username, password)
    time.sleep(60)
    supplier_portal(Retail_link_apps_url)
    for i in df.index:
        print(df["Invoice_No"].loc[i])
        if str(df["Invoice_No"].loc[i])+".xlsx" in downloaded_list:
            continue
        elif df["Promotion_No"].loc[i]=="NAN" or df["Promotion_No"].loc[i]==None or df["Promotion_No"].loc[i]=="" or str(df["Promotion_No"].loc[i])=="nan" or str(df["Deal_Type"].loc[i])=="Fixed Agreement":
            continue
        else:
            try:
                download_excel(df["Promotion_No"].loc[i],str(df["Start_Date"].loc[i]),str(df["End_Date"].loc[i]))
                rename_file(str(df["Invoice_No"].loc[i]))
            except Exception as e:
                print(f"Failed with {df['Invoice_No'].loc[i]}: {e}")
                df.drop([i],inplace = True)
                df.to_csv(r'C:\Users\Python\Desktop\ASDA Images\Scrubbed_Charges\ASDA_Charges.csv',index=False)
                driver.close()
                break


downloaded_list = [file for file in os.listdir(r"C:\Users\python\Desktop\ASDA EXCEL FILES") if os.path.isfile(os.path.join(r"C:\Users\python\Desktop\ASDA EXCEL FILES", file))]
Full_Download(ASDA_Charges,downloaded_list)
