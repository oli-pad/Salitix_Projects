import os
from pathlib import Path
import re
import pdfplumber
import pandas as pd
from collections import namedtuple
import numpy as np
from sys import argv

script,PRF_path,price_file_path,download_path=argv

promo_form_path=PRF_path
#Useful csv
df2=pd.read_csv(price_file_path+"\Sainsbury_Price_File.csv")
#Column Headers
Line=namedtuple('Line','Deleted Post_Deletion_ID Retailer_promotion_number_1 Salitix_client_number Salitix_customer_number Retailer_promotion_number_2 Retailer_promotion_description Promo_period Promo_funding_type Instore_Start_Date Instore_End_Date Buy_In_Start_Date Buy_In_End_Date Outer_Case_Code Retailer_Product_Number Retailer_Product_Number_2	Retailer_Product_Description Retailer_Product_Unit_Size	Retailer_Case_Size Retailer_product_vat_rate Feature_space_fee Positioning_fee Standard_Selling_Price Promotional_Selling_Price Standard_Case_Cost Promotional_Case_Cost Standard_margin_perc Promo_margin_perc Promo_Retro_Funding_Case Promo_Retro_Start_Date Promo_Retro_End_Date Retailer_Promo_Funding_Perc Supplier_Promo_Funding_Perc Trigger_Unit_Qty Trigger_Funding_Amount Epos_Funding_Amount Standard_Volume_Forecast Promo_Volume_Forecast Retail_Promo_Comments Data_Source')
Lines=[]
#Regular expression analysis
#Setting up the searches
Promo_Start_re=re.compile(r'^Promotion Start Date (\d{2})[/](\d{2})[/](\d{4})')
Promo_End_re=re.compile(r'^Promotion End Date (\d{2})[/](\d{2})[/](\d{4})')
Promo_Trigger_Fund_re=re.compile(r'^(\d+)[/](\d+) (\d+) (.*) GBP (\d+)[.](\d+)*')
Promo_Fixed_Total_Net_re=re.compile(r'^Total Amount Excluding VAT: £ (.*).(\d+)')
Promo_Fixed_Total_Gross_re=re.compile(r'^Total Amount Including VAT: £ (.*).(\d+)')
Promo_comments_re=re.compile(r'Promotion Store Format (.*)')
Promo_description_1_re=re.compile(r'Promotion Mechanic (.*)')
Promo_description_2_re=re.compile(r'Promotion Mechanic')

Deleted=None#changed
Post_Deletion_ID=None
Retailer_promotion_number_1=None
Retailer_promotion_number_2=None
Retailer_promotion_description=None#MATCH FROM EXCEL
Promo_period=None#MATCH FROM EXCEL
Promo_funding_type=None
Outer_Case_Code=None
Retailer_Product_Number=None
Retailer_Product_Number_2=None
Retailer_Product_Description=None
Retailer_Product_Unit_Size=None
Retailer_Case_Size=None
Retailer_product_vat_rate=None
Feature_space_fee=None
Positioning_fee=0
Standard_Selling_Price=None
Promotional_Selling_Price=None
Standard_Case_Cost=None
Promotional_Case_Cost=None
Standard_margin_perc=None
Promo_margin_perc=None
Promo_Retro_Funding_Case=None#changed
Promo_Retro_Start_Date=None
Promo_Retro_End_Date=None
Retailer_Promo_Funding_Perc=None
Supplier_Promo_Funding_Perc=None
Trigger_Unit_Qty=None
Trigger_Funding_Amount=None
Epos_Funding_Amount=None
Standard_Volume_Forecast=None
Promo_Volume_Forecast=None
Retail_Promo_Comments=None
Data_Source=None#The file name

def Promotion_number(df):
    complete=[]
    start_dates=df["Instore_Start_Date"]
    end_dates=df["Instore_End_Date"]
    std_case_size=df["Retailer_Case_Size"]
    std_case_cost=df["Standard_Case_Cost"]
    std_selling=df["Standard_Selling_Price"]
    promo_selling=df["Promotional_Selling_Price"]
    trigger_funding=df["Trigger_Funding_Amount"]
    epos_funding=df["Epos_Funding_Amount"]
    No=0
    for i in df.index:
        if i in complete:continue
        pass1=[j for j,x in enumerate(start_dates) if x==start_dates[i]]
        pass2=[j for j,x in enumerate(end_dates) if x==end_dates[i]]
        pass3=[j for j,x in enumerate(std_case_size) if x==std_case_size[i]]
        pass4=[j for j,x in enumerate(std_case_cost) if x==std_case_cost[i]]
        pass5=[j for j,x in enumerate(std_selling) if x==std_selling[i]]
        pass6=[j for j,x in enumerate(promo_selling) if x==promo_selling[i]]
        pass7=[j for j,x in enumerate(trigger_funding) if x==trigger_funding[i]]
        pass8=[j for j,x in enumerate(epos_funding) if x==epos_funding[i]]
        #when the index numbers are shared accross all lists the promotion is the same.
        #identify these numbers by using if in list, and at the end identify what should have the same promo numbers
        #put the index into a completed list and check against this.
        group_index=mulitple_promo(pass1,pass2,pass3,pass4,pass5,pass6,pass7,pass8)
        No+=1
        for j in group_index:
            df['Retailer_promotion_number_1'][j]=No
            complete.append(j)

def mulitple_promo(pass1,pass2,pass3,pass4,pass5,pass6,pass7,pass8):
    group_index=[]
    for i in pass1:
        if i in pass2:
            if i in pass3:
                if i in pass4:
                    if i in pass5:
                        if i in pass6:
                            if i in pass7:
                                if i in pass8:
                                    group_index.append(i)
                                else:continue
                            else:continue
                        else:continue
                    else:continue
                else:continue
            else:continue
        else:continue
    return group_index

def sainos_promo_reader(file,data):
    group=[]
    Data_Source=data
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            if text==None:continue
            for line in text.split('\n'):
                line=" ".join(line.split())
                group.append(line)
                Promo_Start=Promo_Start_re.search(line)
                Promo_End=Promo_End_re.search(line)
                Promo_Trigger_Fund=Promo_Trigger_Fund_re.search(line)
                Promo_Fixed_Total_Net=Promo_Fixed_Total_Net_re.search(line)
                Promo_Fixed_Total_Gross=Promo_Fixed_Total_Gross_re.search(line)
                Promo_comments=Promo_comments_re.search(line)
                Promo_description_1=Promo_description_1_re.search(line)
                Promo_description_2=Promo_description_2_re.search(line)
                if Promo_comments:
                    Retail_Promo_Comments=Promo_comments.group(1)
                elif Promo_description_1:
                    save_re=re.compile(r"Save £(.*)")
                    only_re=re.compile(r"Only £(.*)")
                    Retailer_promotion_description=Promo_description_1.group(1)
                    save=save_re.search(line)
                    only=only_re.search(line)
                    if save:
                        action="save"
                        action_amt=save.group(1)
                    elif only:
                        action="only"
                        action_amt=only.group(1)
                    else:
                        action_amt=None
                elif Promo_description_2 and not Promo_description_1:
                    Retailer_promotion_description=group[-2]
                elif Promo_Start:
                    Instore_Start_Date=Promo_Start.group(1)+"/"+Promo_Start.group(2)+"/"+Promo_Start.group(3)
                    Promo_Retro_Start_Date=Instore_Start_Date
                    Buy_In_Start_Date=Instore_Start_Date
                elif Promo_End:
                    Instore_End_Date=Promo_End.group(1)+"/"+Promo_End.group(2)+"/"+Promo_End.group(3)
                    Promo_Retro_End_Date=Instore_End_Date
                    Buy_In_End_Date=Instore_End_Date
                elif Promo_Trigger_Fund:
                    Promo_funding_type='E'
                    Feature_space_fee=0
                    Trigger_Unit_Qty=1
                    Epos_Funding_Amount=Promo_Trigger_Fund.group(5)+"."+Promo_Trigger_Fund.group(6)
                    Trigger_Funding_Amount=0
                    Retailer_Product_Number=Promo_Trigger_Fund.group(3)
                    if 'Retail_Promo_Comments' not in locals():
                        Retail_Promo_Comments = "Not Found"
                    Lines.append(Line(Deleted,Post_Deletion_ID,Retailer_promotion_number_1,Salitix_client_number,Salitix_customer_number,Retailer_promotion_number_2,Retailer_promotion_description,Promo_period,Promo_funding_type,Instore_Start_Date,Instore_End_Date,Buy_In_Start_Date,Buy_In_End_Date,Outer_Case_Code,Retailer_Product_Number,Retailer_Product_Number_2,Retailer_Product_Description,Retailer_Product_Unit_Size,Retailer_Case_Size,Retailer_product_vat_rate,Feature_space_fee,Positioning_fee,Standard_Selling_Price,Promotional_Selling_Price,Standard_Case_Cost,Promotional_Case_Cost,Standard_margin_perc,Promo_margin_perc,Promo_Retro_Funding_Case,Promo_Retro_Start_Date,Promo_Retro_End_Date,Retailer_Promo_Funding_Perc,Supplier_Promo_Funding_Perc,Trigger_Unit_Qty,Trigger_Funding_Amount,Epos_Funding_Amount,Standard_Volume_Forecast,Promo_Volume_Forecast,Retail_Promo_Comments,Data_Source))
                #    locate=df.loc[df['Retailer_Product_Number']==int(Retailer_Product_Number)]
                #    Retailer_Product_Description=locate['Retailer_Product_Description'].iloc[0]
                    #locate=df3.loc[df3['Retailer_Product_Number']==int(Retailer_Product_Number)]
                    #column=locate.loc[locate["Financial Year"]==int(Year)]
                    #Standard_Selling_Price=column['Retailer_std_Price'].iloc[0]
                    #if action=="save"or action=="Save":
                    #    Promotional_Selling_Price=float(Standard_Selling_Price)-float(action_amt)
                    #elif action=="only"or action=="Only":
                #        Promotional_Selling_Price=action_amt
                  # Lines.append(Line(Deleted,Post_Deletion_ID,Retailer_promotion_number_1,Salitix_client_number,Salitix_customer_number,Retailer_promotion_number_2,Retailer_promotion_description,Promo_period,Promo_funding_type,Instore_Start_Date,Instore_End_Date,Buy_In_Start_Date,Buy_In_End_Date,Outer_Case_Code,Retailer_Product_Number,Retailer_Product_Number_2,Retailer_Product_Description,Retailer_Product_Unit_Size,Retailer_Case_Size,Retailer_product_vat_rate,Feature_space_fee,Positioning_fee,Standard_Selling_Price,Promotional_Selling_Price,Standard_Case_Cost,Promotional_Case_Cost,Standard_margin_perc,Promo_margin_perc,Promo_Retro_Funding_Case,Promo_Retro_Start_Date,Promo_Retro_End_Date,Retailer_Promo_Funding_Perc,Supplier_Promo_Funding_Perc,Trigger_Unit_Qty,Trigger_Funding_Amount,Epos_Funding_Amount,Standard_Volume_Forecast,Promo_Volume_Forecast,Retail_Promo_Comments,Data_Source))
                elif Promo_Fixed_Total_Net:
                    info=group[-3].split(" ")
                    Retailer_Product_Number=info[1]
                    #Feature_space_fee=Promo_Fixed_Total_Net.group(1)+Promo_Fixed_Total_Net.group(2)
                    #Feature_space_fee=Feature_space_fee.replace(",","")
                elif Promo_Fixed_Total_Gross:
                    Promo_funding_type=""
                    Trigger_Unit_Qty=1
                    Trigger_Funding_Amount=0
                    Epos_Funding_Amount=0
                    Feature_space_fee=Promo_Fixed_Total_Gross.group(1)+"."+Promo_Fixed_Total_Gross.group(2)
                    Feature_space_fee=Feature_space_fee.replace(",","")
                    Feature_space_fee=Feature_space_fee.replace(".","",1)
                    Lines.remove(Lines[-1])
                    Lines.append(Line(Deleted,Post_Deletion_ID,Retailer_promotion_number_1,Salitix_client_number,Salitix_customer_number,Retailer_promotion_number_2,Retailer_promotion_description,Promo_period,Promo_funding_type,Instore_Start_Date,Instore_End_Date,Buy_In_Start_Date,Buy_In_End_Date,Outer_Case_Code,Retailer_Product_Number,Retailer_Product_Number_2,Retailer_Product_Description,Retailer_Product_Unit_Size,Retailer_Case_Size,Retailer_product_vat_rate,Feature_space_fee,Positioning_fee,Standard_Selling_Price,Promotional_Selling_Price,Standard_Case_Cost,Promotional_Case_Cost,Standard_margin_perc,Promo_margin_perc,Promo_Retro_Funding_Case,Promo_Retro_Start_Date,Promo_Retro_End_Date,Retailer_Promo_Funding_Perc,Supplier_Promo_Funding_Perc,Trigger_Unit_Qty,Trigger_Funding_Amount,Epos_Funding_Amount,Standard_Volume_Forecast,Promo_Volume_Forecast,Retail_Promo_Comments,Data_Source))

def cpc_adding(df1,df2):
    prod_list=df2['Product_No'].tolist()
    for i in df1.index:
        prod=df1['Retailer_Product_Number'][i]
        print(prod)
        if int(prod) not in prod_list:continue
        locate=df2.loc[df2['Product_No']==int(prod)]
        dates=locate["Effective_Date"].tolist()
        dates_index=list_duplicates_of(dates,max(dates))
        recent_index=max(dates_index)
        list1=locate["Std_case_cost"].tolist()
        list2=locate["Std_case_size"].tolist()
        list3=locate["VAT"].tolist()
        df1["Standard_Case_Cost"][i]=list1[recent_index]
        df1["Retailer_Case_Size"][i]=list2[recent_index]
        df1["Retailer_product_vat_rate"][i]=list3[recent_index]
        if df1["Promo_funding_type"][i]=="E":
            df1["Promotional_Case_Cost"][i]=list1[recent_index]
        else:
            print("ERROR: new funding type")


def data_extraction(path):
    for filename in listdir_nohidden(path):
        if filename=="Thumbs.db":continue
        print(filename)
        Data_Source=filename
        sainos_promo_reader(os.path.join(path,filename),Data_Source)

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

def into_data_frame(lines,df2):
    df1=pd.DataFrame(lines)
    Promotion_number(df1)
    cpc_adding(df1,df2)
    #no products here????
    df1.index=np.arange(1, len(df1)+1)
    df1.index.name='ID_Pivot'
    df1.to_csv(download_path+'\Promo_form.csv',index=True)

def list_duplicates_of(seq,item):
    start_at = -1
    locs = []
    while True:
        try:
            loc = seq.index(item,start_at+1)
        except ValueError:
            break
        else:
            locs.append(loc)
            start_at = loc
    return locs

Salitix_client_number=input("Client number? ")
Salitix_customer_number="SAI01"
Year=""

data_extraction(promo_form_path)
into_data_frame(Lines,df2)
