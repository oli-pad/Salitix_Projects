import os
from sys import argv

script,text=argv

def main():
    client_list=text.split(" / ")
    os.system(r"python C:\Users\python\Desktop\projects\web_portal_scraping\Sainsbury_Salesforce\sainsbury_salesforce.py {} {}".format(client_list[1],client_list[2]))

if __name__ == "__main__":
    main()