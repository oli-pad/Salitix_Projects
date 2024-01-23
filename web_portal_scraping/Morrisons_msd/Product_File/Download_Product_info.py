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

#Product File
df2=pd.read_csv(r"C:\Users\python\Desktop\projects\web_portal_scraping\Morrisons_msd\Product_File\Product_List.csv")

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


#adapt for product number
def item_no(item):
    driver.get("https://supplier.morrisons.com/webui/SupplierWebUI/?code=4/0AWgavdfm9LfpbQqei_9ERlmFg-mfxRg9twkiCyADeBf7aJCWqzCL4Yrk2iG7wlCUGn5M3A&scope=profile%20https://www.googleapis.com/auth/userinfo.profile#deepLink=1&contextID=EnglishUK&workspaceID=Main&screen=homepage")
    time.sleep(15)
    driver.find_element(By.XPATH,"//div[@title='Item Search']").click()
    time.sleep(15)
    driver.find_element(By.XPATH,"(//input[@class='stb-SearchBox'])[1]").clear()
    time.sleep(5)
    driver.find_element(By.XPATH,"(//input[@class='stb-SearchBox'])[1]").send_keys(item)
    time.sleep(15)
    driver.find_element(By.XPATH,"//button[@class='stibo-GraphicsButton SearchButton']").click()
    time.sleep(15)

#adapt to get product number
def scrape_page(ID):
    time.sleep(15)
    WebDriverWait(driver,150).until(EC.presence_of_element_located((By.XPATH,"(//span[@class='gwt-InlineLabel'])[1]")))
    driver.find_element(By.XPATH,"(//span[@class='gwt-InlineLabel'])[1]").click()
    time.sleep(15)
    try:
        Start_Date=driver.find_element(By.XPATH,"(//div[@class='gwt-HTML'])[21]").text
        End_Date=driver.find_element(By.XPATH,"(//div[@class='gwt-HTML'])[22]").text
    except:
        Start_Date=driver.find_element(By.XPATH,"(//div[@class='gwt-HTML'])[20]").text
        End_Date=driver.find_element(By.XPATH,"(//div[@class='gwt-HTML'])[21]").text
    driver.find_element(By.XPATH,"(//span[@class='gwt-InlineLabel'])[3]").click()
    time.sleep(60)
    soup=BeautifulSoup(driver.page_source,"html.parser")
    for tr in soup.find_all('tr')[5:]:
        line=[td.get_text() for td in tr]
        if len(line)>=10 and str(line[0])!="Item Number":
            Promo_df.loc[len(Promo_df.index)] = [line[0],line[1].replace("MIN: ",""),line[3],line[4],line[5],line[9],Start_Date,End_Date,ID]


def run(file):
    df=pd.read_csv(file)
    login("",email,password)
    time.sleep(60)
    for i in df.index:
        if "Agreement.Promotion" in df["ID"].iloc[i] and df["ID"].iloc[i] not in df2["ID"].values:
            if "Confirmed" in df["Status"].iloc[i]:
                print(df["ID"].iloc[i])
                agreement_numbers(df["ID"].iloc[i])
                scrape_page(df["ID"].iloc[i])
                Promo_df.to_csv("Morrisons_Promo_Schedule.csv", index=False)


run(r"C:\Users\Python\Desktop\projects\web_portal_scraping\Morrisons_msd\Agreements.csv")
