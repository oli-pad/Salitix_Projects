import pyodbc
import pandas as pd
import numpy as np

SI_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=CL002_Pladis_Processed;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
SI_cursor = SI_conn.cursor()

Customer_Charges_Query="SELECT * FROM [CL002_Pladis_Processed].[dbo].[vw_SAL_Customer_Charges_Alt]"

Customer_Charges_df=pd.read_sql(Customer_Charges_Query,SI_conn)

Exceptions_report=[]#columnns=['Retailer_Invoice','Nett_Amount','Gross_Amount','Reason'])

def Transposition_9(customer_charges):
    for i in customer_charges.index:
        for j in customer_charges.index:
            if i!=j and customer_charges['Retailer_Invoice'][i]!=customer_charges['Retailer_Invoice'][j] and customer_charges['Salitix_Customer_Number'][i]==customer_charges['Salitix_Customer_Number'][j]:
                if customer_charges['Nett_Amount'][i]!=customer_charges['Nett_Amount'][j] and customer_charges['Gross_Amount'][i] != customer_charges['Gross_Amount'][j]:
                    if days_between(customer_charges['Document_Date'][i], customer_charges['Document_Date'][j])<=45:
                        if check_transposition(customer_charges['Nett_Amount'][i],customer_charges['Nett_Amount'][j]):
                            Exceptions_report.append([customer_charges['Salitix_Customer_Number'][i],customer_charges['Retailer_Invoice'][i],customer_charges['Nett_Amount'][i],customer_charges['Gross_Amount'][i],"Nett Check",customer_charges['Invoice_Line_Description'][i],customer_charges['Comments'][i]])
                            Exceptions_report.append([customer_charges['Salitix_Customer_Number'][j],customer_charges['Retailer_Invoice'][j],customer_charges['Nett_Amount'][j],customer_charges['Gross_Amount'][j],"Nett Check",customer_charges['Invoice_Line_Description'][j],customer_charges['Comments'][j]])
                        elif check_transposition(customer_charges['Gross_Amount'][i],customer_charges['Gross_Amount'][j]):
                            Exceptions_report.append([customer_charges['Salitix_Customer_Number'][i],customer_charges['Retailer_Invoice'][i],customer_charges['Nett_Amount'][i],customer_charges['Gross_Amount'][i],"Gross Check",customer_charges['Invoice_Line_Description'][i],customer_charges['Comments'][i]])
                            Exceptions_report.append([customer_charges['Salitix_Customer_Number'][j],customer_charges['Retailer_Invoice'][j],customer_charges['Nett_Amount'][j],customer_charges['Gross_Amount'][j],"Gross Check",customer_charges['Invoice_Line_Description'][j],customer_charges['Comments'][j]])
        df = pd.DataFrame(Exceptions_report)
        df.to_csv('Transposition_9.csv',index=False)

from itertools import permutations

def check_transposition(num1, num2):
    if sorted(str(num1)) == sorted(str(num2)):
        if abs(float(num1)-float(num2))%9==0:
            return True
        else:
            return False
    else:
        return False
    
from datetime import date

def days_between(d1, d2):
    d1 = date.fromisoformat(str(d1)[:10])
    d2 = date.fromisoformat(str(d2)[:10])
    delta = d2 - d1
    return delta.days

Transposition_9(Customer_Charges_df)

df = pd.DataFrame(Exceptions_report)
df.to_csv('Transposition_9.csv',index=False)