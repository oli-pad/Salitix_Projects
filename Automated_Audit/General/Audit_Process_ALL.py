import os
import pyodbc
import pandas as pd
# importing sys
from sys import argv

Alt_Client_List=["CL001","CL002","CL003","CL005","CL012","CL014","CL020","CL023","CL027","CL029"]

Retailer_List=["ASD01","MOR01","SAI01","TES01","WAI01","ICE01","AMA01","NIS01","SUP01"]

generate_arg='python Promo_reconciliation.py {} {} {} {} {}'

Date_period_1='2021-01-01'
Date_period_2='2024-02-01'

for i in Alt_Client_List:
    for x in Retailer_List:
        print(i,x)
        os.system(generate_arg.format(i,x,Date_period_1,Date_period_2,'Y'))

#for i in Ftd_Client_List:
 #   for x in Retailer_List:
   #     if x=="ASD01":
    #        os.system(generate_arg.format(i,x,Date_period_1,Date_period_2,'Y'))
     #   else:
     #       os.system(generate_arg.format(i,x,Date_period_1,Date_period_2,'N'))
