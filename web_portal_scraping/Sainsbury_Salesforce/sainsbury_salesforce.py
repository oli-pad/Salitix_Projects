import requests
import pandas as pd
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pyautogui
from sys import argv
options = webdriver.ChromeOptions()
options.add_argument("download.default_directory=C:/Documents, download.prompt_for_download=False")
driver = webdriver.Chrome(options=options)

script,email,password=argv

def login(url,usernameId, username, passwordId, password, submit_buttonId):
   driver.get(url)
   driver.find_element(By.ID,usernameId).send_keys(username)
   time.sleep(5)
   driver.find_element(By.ID,passwordId).send_keys(password)
   time.sleep(10)
   driver.find_element(By.XPATH,"//input[@value='Login']").click()
   time.sleep(5)


def new_line_form():
    driver.find_element(By.XPATH,"//a[@title='New Lines Tab']").click()
    driver.find_element(By.XPATH,"//input[@name='go']").click()

def NLF_table_status(soup):
    NLF_df=pd.DataFrame(columns=['New Line Name', 'NLF Stage'])
    col1=[]
    col2=[]
    for tr in soup.find_all('tr')[5:]:
        line=[td.get_text() for td in tr]
        col1.append(line[1])
        col2.append(line[2])
    NLF_df['New Line Name']=col1
    NLF_df['NLF Stage']=col2
    return NLF_df

def NLF_download_list(soup,name):
    NLF_href_list=[]
    NLF_df=NLF_table_status(soup)
    for i in soup.find_all('a'):
        if "NLF-" in i.text and i.text not in name:
            status=NLF_df.loc[NLF_df['New Line Name']==i.text]
            
            print(i.text[4:11])
            if i.text[4:8]!="2017":None
            name.append(i.text)
            if status['NLF Stage'].values[0]=='E-form Completed':
                NLF_href_list.append(i['href'])
    for i in soup.find_all('a'):
        if i.text=='Next Page>':
            next_page_href=i['href']
            driver.get(sainsbury_webpage+next_page_href)
            soup=BeautifulSoup(driver.page_source,"html.parser")
            list=NLF_download_list(soup,name)
            for i in list:
                NLF_href_list.append(i)
            break
        elif i.text=='<Previous Page':
            None
    return NLF_href_list

#completed, next stage is cpc
def NLF_download_pdf(soup):
    NLF_list=NLF_download_list(soup,[])
    for i in NLF_list:
        try:
            driver.get(sainsbury_webpage+i)
        except:None
        soup=BeautifulSoup(driver.page_source,"html.parser")
        pdf_links=soup.find_all("input", {"value": "View PDF"})[0]
        pdf=re.findall("([^']*)",str(pdf_links["onclick"]))
        time.sleep(1)
        driver.get(pdf[2])
        time.sleep(2)
        pyautogui.hotkey('ctrl','s')
        time.sleep(2)
        pyautogui.press('enter')
        time.sleep(2)

def cost_price_change():
    driver.find_element(By.XPATH,"//a[@title='Cost Price  Changes Tab']").click()
    driver.find_element(By.XPATH,"//input[@name='go']").click()

def CPC_table_status(soup):
    CPC_df=pd.DataFrame(columns=['Cost Change Name', 'CPC Stage'])
    col1=[]
    col2=[]
    for tr in soup.find_all('tr')[5:]:
        line=[td.get_text() for td in tr]
        col1.append(line[1])
        col2.append(line[2])
    CPC_df['Cost Change Name']=col1
    CPC_df['CPC Stage']=col2
    return CPC_df

def CPC_download_list(soup,name):
    CPC_href_list=[]
    CPC_df=CPC_table_status(soup)
    for i in soup.find_all('a'):
        if "CPC-" in i.text and i.text not in name:
            status=CPC_df.loc[CPC_df['Cost Change Name']==i.text]
            name.append(i.text)
            if status['CPC Stage'].values[0]=='E-form Completed':
                CPC_href_list.append(i['href'])
    for i in soup.find_all('a'):
        if i.text=='Next Page>':
            next_page_href=i['href']
            driver.get(sainsbury_webpage+next_page_href)
            soup=BeautifulSoup(driver.page_source,"html.parser")
            list=CPC_download_list(soup,name)
            for i in list:
                CPC_href_list.append(i)
            break
        elif i.text=='<Previous Page':
            None#need to think about this can be affected.
    return CPC_href_list

def CPC_download_pdf(soup):
    CPC_list=CPC_download_list(soup,[])
    for i in CPC_list:
        driver.get(sainsbury_webpage+i)
        soup=BeautifulSoup(driver.page_source,"html.parser")
        pdf_links=soup.find_all("input", {"value": "View PDF"})[0]
        pdf=re.findall("([^']*)",str(pdf_links["onclick"]))
        time.sleep(1)
        driver.get(pdf[2])
        time.sleep(2)
        pyautogui.hotkey('ctrl','s')
        time.sleep(2)
        pyautogui.press('enter')
        time.sleep(2)

def promotion_form():
    driver.find_element(By.XPATH,"//a[@title='Promotion Forms Tab']").click()
    driver.find_element(By.XPATH,"//input[@name='go']").click()

def PRF_table_status(soup):
    PRF_df=pd.DataFrame(columns=['Promotion Form Name', 'PRF Stage'])
    col1=[]
    col2=[]
    for tr in soup.find_all('tr')[5:]:
        line=[td.get_text() for td in tr]
        col1.append(line[1])
        col2.append(line[3])
    PRF_df['Promotion Form Name']=col1
    PRF_df['PRF Stage']=col2
    return PRF_df

def PRF_download_list(soup,name):
    PRF_href_list=[]
    PRF_df=PRF_table_status(soup)
    print(PRF_df)
    for i in soup.find_all('a'):
        if "PRF-" in i.text and i.text not in name:
            year=i.text
            if year[4:11]=='2023-05': #or int(year[4:8])==2021:
                status=PRF_df.loc[PRF_df['Promotion Form Name']==i.text]
                name.append(i.text)
                try:
                    if status['PRF Stage'].values[0]=='E-form Completed':
                        PRF_href_list.append(i['href'])
                except:
                    None
    for i in soup.find_all('a'):
        if i.text=='Next Page>':
            next_page_href=i['href']
            driver.get(sainsbury_webpage+next_page_href)
            soup=BeautifulSoup(driver.page_source,"html.parser")
            list=PRF_download_list(soup,name)
            for i in list:
                PRF_href_list.append(i)
            break
        elif i.text=='<Previous Page':
            None
    return PRF_href_list

def PRF_download_pdf(soup):
    PRF_list=PRF_download_list(soup,[])
    for i in PRF_list:
        driver.get(sainsbury_webpage+i)
        soup=BeautifulSoup(driver.page_source,"html.parser")
        pdf_links=soup.find_all("input", {"value": "View PDF"})[0]
        pdf=re.findall("([^']*)",str(pdf_links["onclick"]))
        time.sleep(1)
        driver.get(pdf[2])
        time.sleep(2)
        pyautogui.hotkey('ctrl','s')
        time.sleep(2)
        pyautogui.press('enter')
        time.sleep(2)

sainsbury_salesforce_webpage_login="https://login.salesforce.com/secur/login_portal.jsp?orgId=00D20000000Kvi3&portalId=060200000000sY1"
sainsbury_salesforce_webpage_login_response = requests.get(sainsbury_salesforce_webpage_login)
sainsbury_webpage='https://sainsburys-eforms.my.salesforce.com/'

login(sainsbury_salesforce_webpage_login,"username",email,"password",password,"Login")

new_line_form()
logged_in_salesforce=driver.page_source
soup = BeautifulSoup(logged_in_salesforce, "html.parser")
NLF_download_pdf(soup)
# driver.get("https://sainsburys-eforms.my.salesforce.com/home/home.jsp")
# cost_price_change()
# logged_in_salesforce=driver.page_source
# soup = BeautifulSoup(logged_in_salesforce, "html.parser")
# CPC_download_pdf(soup)
# driver.get("https://sainsburys-eforms.my.salesforce.com/home/home.jsp")
# promotion_form()
# logged_in_salesforce=driver.page_source
# soup = BeautifulSoup(logged_in_salesforce, "html.parser")
# PRF_download_pdf(soup)
driver.close()
driver.quit()
