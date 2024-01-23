import os
import pyodbc
import pandas as pd
# importing sys
from sys import argv

Client_List=["CL001","CL002","CL003","CL005","CL012","CL013","CL014","CL020","CL023","CL026","CL027","CL028","CL029","CL031"]

Retailer_List=["ASD01","MOR01","SAI01","TES01","WAI01","ICE01","AMA01","NIS01"]

generate_arg='python Promo_reconciliation.py {} {} {} {} {}'

Client_Code=input("What's the Client Code?  > ")
Retailer_Code=input("What's the Retailer Code?  > ")
Date_period_1=input("Start date?  > ")
Date_period_2=input("End date?  > " )
SCC_alt=input("Has client moved to SCC_alt?    [Y/N]    > ")

os.system(generate_arg.format(Client_Code,Retailer_Code,Date_period_1,Date_period_2,SCC_alt))
