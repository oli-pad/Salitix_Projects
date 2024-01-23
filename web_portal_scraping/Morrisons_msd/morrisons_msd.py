import requests
import pandas as pd
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sys import argv
options = webdriver.ChromeOptions()
options.add_argument("download.default_directory=C:/Documents, download.prompt_for_download=False")
driver = webdriver.Chrome(options=options)

script,email,password=argv
#list to search through for promotions
searches=[ "2021-01","2021-02","2021-03","2021-04","2021-05",
    "2021-06","2021-07","2021-08","2021-09","2021-10",
    "2021-11","2021-12","2022-01","2022-02","2022-03","2022-04","2022-05",
    "2022-06","2022-07","2022-08","2022-09","2022-10",
    "2022-11","2022-12"]
#Function to open the log in page and follow  the nesercary steps.
#There is a 2FA with these accounts so this will take that in account with input.
def login(url,email,password):
    #url for log on page.
    driver.get("https://accounts.google.com/o/oauth2/auth/identifier?access_type=offline&approval_prompt=force&scope=profile&response_type=code&redirect_uri=https%3A%2F%2Fsupplier.morrisons.com%2Fwebui%2FSupplierWebUI%2F&client_id=32583736216-28673lub3cjgr3u93e4f9avc7a805kcm.apps.googleusercontent.com&flowName=GeneralOAuthFlow")
    driver.find_element(By.ID,"identifierId").send_keys(email)
    driver.find_element(By.XPATH,"//span[text()='Next']").click()
    time.sleep(3)
    #WebDriverWait(driver,150).until(EC.presence_of_element_located((By.XPATH,"//input[@name='password']")))
    #driver.find_element(By.XPATH,"//input[@name='password']").send_keys(password)
    #driver.find_element(By.ID,"passwordNext").click()
    twoFA=input("2FA > ")
    if twoFA != "":
        driver.find_element(By.ID,"idvPin").send_keys(twoFA)
        driver.find_element(By.XPATH,"//span[text()='Next']").click()

def agreement_numbers(YYYYMM):
    agreements_df=pd.DataFrame(columns=['ID','Status'])
    driver.get("https://supplier.morrisons.com/webui/SupplierWebUI/?code=4/0AdQt8qimQZ1ekvvuqamhMeWsC4YAVuDFltCnfB4hubM2hJFpzUeaVJfTtSPjvwiGqwk5Jw&scope=profile%20https://www.googleapis.com/auth/userinfo.profile#deepLink=1&contextID=EnglishUK&workspaceID=Main&screen=homepage")
    time.sleep(15)
    driver.find_element(By.XPATH,"//div[@title='Agreement Search']").click()
    time.sleep(15)
    driver.find_element(By.XPATH,"(//input[@class='stb-SearchBox'])[2]").clear()
    time.sleep(5)
    driver.find_element(By.XPATH,"(//input[@class='stb-SearchBox'])[2]").send_keys(YYYYMM)
    time.sleep(15)
    driver.find_element(By.XPATH,"//button[@class='stibo-GraphicsButton SearchButton']").click()
    WebDriverWait(driver,150).until(EC.presence_of_element_located((By.ID,"ListTable")))
    col1=[]
    col2=[]
    time.sleep(60)
    soup=BeautifulSoup(driver.page_source,"html.parser")
    for tr in soup.find_all('tr')[5:]:
        line=[td.get_text() for td in tr]
        print(line)
        col1.append(line[0])
        col2.append(line[3])
    agreements_df['ID']=col1
    agreements_df['Status']=col2
    time.sleep(30)
    return agreements_df

def agreement_list(searches):
    time.sleep(60)
    all_agreements_df=pd.DataFrame(columns=['ID','Status'])
    for i in searches:
        print(i)
        all_agreements_df=pd.concat([all_agreements_df,agreement_numbers(i)], ignore_index=True)
        all_agreements_df.to_csv("Agreements.csv",index=True)
    return all_agreements_df


login("",email,password)
df=agreement_list(searches)
df.to_csv("Agreements.csv",index=True)
