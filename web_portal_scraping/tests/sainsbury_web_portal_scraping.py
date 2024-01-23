import requests
import pandas as pd
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pyautogui
options = webdriver.ChromeOptions()
options.add_argument("download.default_directory=C:/Documents, download.prompt_for_download=False")
driver = webdriver.Chrome(options=options)
login_details={"username":"Kirsten.Flynn@edrington.com","password":"Grouse@01"}

def login(url,usernameId, username, passwordId, password, submit_buttonId):
   driver.get(url)
   driver.find_element(By.ID,usernameId).send_keys(username)
   driver.find_element(By.ID,passwordId).send_keys(password)
   driver.find_element(By.XPATH,"//input[@value='Login']").click()


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
            break
    return NLF_href_list
#completed, next stage is cpc
def NLF_download_pdf(soup):
    NLF_list=NLF_download_list(soup,[])
    for i in NLF_list:
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

login(sainsbury_salesforce_webpage_login,"username","Kirsten.Flynn@edrington.com","password","Grouse@01","Login")
#new_line_form()
logged_in_salesforce=driver.page_source
soup = BeautifulSoup(logged_in_salesforce, "html.parser")
#NLF_download_pdf(soup)


#need to figure out how to download HTML as pdf's however seems to just need admin pw.

#the browser now contains the cookies generated from the authentication
#driver.close()
#driver.quit()
