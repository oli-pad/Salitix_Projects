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

Price_df=pd.DataFrame(columns=["Cost_Effective_Date","Price_Description","Item_Number","Product_Number","Case_Size","Current_Case_Cost","Proposed_Case_Cost","Status","ID","Product_Description","CRP_ID"])
#df2=pd.read_csv(r"C:\Users\Python\Desktop\projects\web_portal_scraping\Morrisons_msd\Morrisons_Promo_Schedule.csv")
#Price_df=df2
def login(url,email,password):
    #url for log on page.
    driver.get("https://accounts.google.com/o/oauth2/auth/identifier?access_type=offline&approval_prompt=force&scope=profile&response_type=code&redirect_uri=https%3A%2F%2Fsupplier.morrisons.com%2Fwebui%2FSupplierWebUI%2F&client_id=32583736216-28673lub3cjgr3u93e4f9avc7a805kcm.apps.googleusercontent.com&flowName=GeneralOAuthFlow")
    driver.find_element(By.ID,"identifierId").send_keys(email)
    driver.find_element(By.XPATH,"//span[text()='Next']").click()
    time.sleep(10)
    WebDriverWait(driver,150).until(EC.presence_of_element_located((By.XPATH,"//input[@name='password']")))
    driver.find_element(By.XPATH,"//input[@name='password']").send_keys(password)
    driver.find_element(By.ID,"passwordNext").click()
    twoFA=input("2FA > ")
    if twoFA != "":
        driver.find_element(By.ID,"idvPin").send_keys(twoFA)
        driver.find_element(By.XPATH,"//span[text()='Next']").click()

def agreement_numbers(agr_number):
    driver.get("https://supplier.morrisons.com/webui/SupplierWebUI/?code=4/0AdQt8qimQZ1ekvvuqamhMeWsC4YAVuDFltCnfB4hubM2hJFpzUeaVJfTtSPjvwiGqwk5Jw&scope=profile%20https://www.googleapis.com/auth/userinfo.profile#deepLink=1&contextID=EnglishUK&workspaceID=Main&screen=homepage")
    time.sleep(15)
    driver.find_element(By.XPATH,"//div[@title='Agreement Search']").click()
    time.sleep(15)
    driver.find_element(By.XPATH,"(//input[@class='stb-SearchBox'])[1]").clear()
    time.sleep(5)
    driver.find_element(By.XPATH,"(//input[@class='stb-SearchBox'])[1]").send_keys(agr_number)
    time.sleep(15)
    driver.find_element(By.XPATH,"//button[@class='stibo-GraphicsButton SearchButton']").click()
    time.sleep(15)

def scrape_page(ID):
    WebDriverWait(driver,150).until(EC.presence_of_element_located((By.XPATH,"(//span[@class='gwt-InlineLabel'])[1]")))
    try:
        driver.find_element(By.XPATH,"(//span[@class='gwt-InlineLabel'])[1]").click()
    except:None
    time.sleep(15)
    Cost_Effective_Date=driver.find_element(By.XPATH,"(//div[@class='gwt-HTML'])[12]").text
    Price_Description=driver.find_element(By.XPATH,"(//div[@class='gwt-HTML'])[13]").text
    driver.find_element(By.XPATH,"(//span[@class='gwt-InlineLabel'])[3]").click()
    time.sleep(60)
    soup=BeautifulSoup(driver.page_source,"html.parser")
    for tr in soup.find_all('tr')[5:]:
        line=[td.get_text() for td in tr]
        if len(line)>=13 and str(line[0])!="Item Number":
            Price_df.loc[len(Price_df.index)] = [Cost_Effective_Date,Price_Description,line[0],line[1],line[3],line[4],line[8],line[11],ID,line[2],line[12]]

def run(file):
    df=pd.read_csv(file)
    #df2=pd.read_csv(r"C:\Users\Python\Desktop\projects\web_portal_scraping\Morrisons_msd\CPC\Morrisons_Price_File.csv")
    login("",email,password)
    time.sleep(60)
    for i in df.index:
        if "Agreement.CostPriceChange" in df["ID"].iloc[i]:# and df["ID"].iloc[i] not in df2["ID"].values:
            if df["Status"].iloc[i]=="Completed":
                agreement_numbers(df["ID"].iloc[i])
                scrape_page(df["ID"].iloc[i])
                Price_df.to_csv("Morrisons_Price_File.csv", index=False)

run(r"C:\Users\Python\Desktop\projects\web_portal_scraping\Morrisons_msd\Agreements.csv")
