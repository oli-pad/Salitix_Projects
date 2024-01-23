
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from pathlib import Path
import shutil
from sys import argv
import time

script,username,password,client=argv

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

Tesco_toolkit=r'https://partnerstoolkit.tesco.com/sign-in/?url=%2Ftoolkit%2F'
Tesco_Cost_page=r"https://toolkit.tesco.com/cost/"

###Functions for Tesco Toolkit
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
   driver.find_element(By.XPATH,"//button[@class='styled__BaseButton-sc-3mnirm-0 styled__PrimaryButton-sc-3mnirm-2 infIji fpiEaX styled__StyledButton-cwBOsQ iGyYrl beans-button__container']").click()
   #time.sleep(10)

def runthrough(url,username,password):
    login(url,username,password)
    time.sleep(5)
    driver.get(Tesco_Cost_page)
    time.sleep(5)
    WebDriverWait(driver,150).until(EC.presence_of_element_located((By.ID,"supplier-search-input")))
    driver.find_element(By.ID,"supplier-search-input").click()
    time.sleep(5)
    if client=="MAXXIUM" or client=="BACARDI" or client=="PREMIER_FOODS":
        driver.find_element(By.ID,"supplier-search-input_listbox_active_option").click()
        time.sleep(5)
    driver.find_element(By.ID,"supplier-search-input_listbox_active_option").click()
    time.sleep(5)
    driver.find_element(By.ID,"search-button").click()
    time.sleep(10)
    driver.find_element(By.XPATH,"//div[@class='sc-jdhwqr fwivnl']").click()
    time.sleep(5)
    driver.find_element(By.XPATH,"//span[@class='sc-dUbtfd sc-gyElHZ fpFkbH fvINNW beans-button__inner-container']").click()
    time.sleep(5)
    driver.find_element(By.XPATH,"//span[@class='sc-dYtuZ sc-gDGHff fBbdRO brDrnc beans-checkbox-with-label__checkbox beans-checkbox__container']").click()
    time.sleep(10)
    driver.find_element(By.XPATH,"//div[@class='sc-jdhwqr ioESas']").click()
    time.sleep(5)
    driver.find_element(By.XPATH,"//button[@class='sc-fIosxK sc-gjNHFA btsWiG cEEWIE sc-hRMJXU kqDOiT beans-button__container']").click()
    time.sleep(5)
    driver.find_element(By.ID,"range").click()
    time.sleep(30)
    #driver.find_element(By.XPATH,"//button[@class='sc-gIBqdA sc-jKTccl fzmXwK vmbbB beans-date-picker__calendar-button beans-button__container']").click()
    #time.sleep(5)
    #for i in range(30):
    #    driver.find_element(By.XPATH,"//svg[@class='sc-hYQoXb ewwWsQ beans-single-calendar__icon-prev beans-icon__svg']").click()
    #    time.sleep(5)
    #driver.find_element(By.XPATH,"//div[@class='sc-ciFQTS ekAzpl']").click()
    #time.sleep(5)
#    driver.find_element(By.XPATH,"//span[@class='sc-clIzBv sc-fyrocj cXQaNS NXLIk beans-button__inner-container']").click()
#    time.sleep(5)
#    driver.find_element(By.XPATH,"//div[@class='sc-ciFQTS ekAzpl']").click()
#    time.sleep(5)
#    driver.find_element(By.XPATH,"//button[@class='sc-fIosxK sc-gjNHFA btsWiG cEEWIE sc-dwsnSq sc-eldieg ekIhvQ kijmjG beans-button__container']").click()
#    time.sleep(300)
#


def file_rename():
    download_name="myProduct_ Cost extract.xls"
    new_name="TESCO_PRICE_FILE_{}.xls"
    os.rename(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),download_name),os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),new_name.format(client)))
    shutil.move(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),new_name.format(client)),os.path.join("Z:\Pricing",new_name.format(client)))

###Run
runthrough(Tesco_toolkit,username,password)
file_rename()
