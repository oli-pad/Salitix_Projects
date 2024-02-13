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
import xlrd

options = webdriver.ChromeOptions()
options.add_argument("download.default_directory=C:/Documents, download.prompt_for_download=False")
driver = webdriver.Chrome(options=options)

script,email,password=argv

df1 = pd.read_csv(r"C:\Users\Python\Desktop\projects\web_portal_scraping\Morrisons_msd\Agreements.csv")
df2=pd.read_csv(r"C:\Users\Python\Desktop\projects\web_portal_scraping\Morrisons_msd\Morrisons_Promo_Schedule.csv")


def check_promo():
    promo_IDs=df1["ID"].unique()
    for i in df2.index:
        if df2["ID"].iloc[i] in promo_IDs:
            return True
    return False

if check_promo() ==  False:
    df2=pd.DataFrame(columns=["Item Number","Product Description","Vendor Product Number","Funding per Unit","Promotional Case Cost","Promtional Retail Price","Start Date","End Date","ID"])
    df2.to_csv("Morrisons_Promo_Schedule.csv", index=False)

Promo_df=pd.DataFrame(columns=["Item Number","Product Description","Vendor Product Number","Funding per Unit","Promotional Case Cost","Promtional Retail Price","Start Date","End Date","ID"])
Promo_df=df2

def login(url,email,password):
    #url for log on page.
    driver.get("https://accounts.google.com/o/oauth2/auth/identifier?access_type=offline&approval_prompt=force&scope=profile&response_type=code&redirect_uri=https%3A%2F%2Fsupplier.morrisons.com%2Fwebui%2FSupplierWebUI%2F&client_id=32583736216-28673lub3cjgr3u93e4f9avc7a805kcm.apps.googleusercontent.com&flowName=GeneralOAuthFlow")
    driver.find_element(By.ID,"identifierId").send_keys(email)
    driver.find_element(By.XPATH,"//span[text()='Next']").click()
    time.sleep(10)
    WebDriverWait(driver,150).until(EC.presence_of_element_located((By.XPATH,"//input[@type='password']")))
    driver.find_element(By.XPATH,"//input[@type='password']").send_keys(password)
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

def reformat_Dates(filepath):
    df = pd.read_csv(filepath)
    for i in df.index:
        start = df["Start Date"].iloc[i]
        try:
            df["Start Date"].iloc[i] = start.split("/")[1] + "/" + start.split("/")[0] + "/" + start.split("/")[2]
        except:
            None
        end = df["End Date"].iloc[i]
        try:df["End Date"].iloc[i] = end.split("/")[1] + "/" + end.split("/")[0] + "/" + end.split("/")[2]
        except:None
        df.to_csv("Morrisons_Promo_Schedule_Dates.csv", index=False)



run(r"C:\Users\Python\Desktop\projects\web_portal_scraping\Morrisons_msd\Agreements.csv")
reformat_Dates(r"C:\Users\Python\Desktop\projects\web_portal_scraping\Morrisons_msd\Morrisons_Promo_Schedule.csv")

