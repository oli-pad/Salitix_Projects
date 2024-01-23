import pyodbc
import pandas as pd
import numpy as np

SI_conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=CL020_Premier_Foods_Processed;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
SI_cursor = SI_conn.cursor()

Customer_Charges_Query="SELECT * FROM [CL020_Premier_Foods_Processed].[dbo].[vw_SAL_Customer_Charges_Alt]"

Customer_Charges_df=pd.read_sql(Customer_Charges_Query,SI_conn)

Exceptions_report=[]#columnns=['Retailer_Invoice','Nett_Amount','Gross_Amount','Reason'])

def VAT_Int_check(customer_charges):
    for i in customer_charges.index:
        #check if gross amount is a integer
        if customer_charges['Gross_Amount'][i]%1==0:
            #check if vat amount is 0
            if customer_charges['VAT'][i]==0:
                Exceptions_report.append([customer_charges['Salitix_Customer_Number'][i],customer_charges['Retailer_Invoice'][i],customer_charges['Nett_Amount'][i],customer_charges['Gross_Amount'][i],"Gross Amount is an integer",customer_charges['Invoice_Line_Description'][i],customer_charges['Comments'][i]])


VAT_Int_check(Customer_Charges_df)

df = pd.DataFrame(Exceptions_report)
df.to_csv('VAT_Int_Check.csv',index=False)