import os
from pathlib import Path
import re
import pdfplumber
import pandas as pd
from collections import namedtuple
import numpy as np
from sys import argv

Line=namedtuple('Line','Product_No Effective_Date std_case_size current_cost std_case_cost VAT')
lines=[]



cpc_from_path=r'C:\Users\Email\Desktop\Oli PDF\PDF Reader\Promo Schedule Automation\SAINSBURY\CPC_forms'
nlf_from_path=r'C:\Users\Email\Desktop\Oli PDF\PDF Reader\Promo Schedule Automation\SAINSBURY\NLF_Forms'
#CPC Regular Expression compile
effective_date_re=re.compile(r'Effective Date (\d{2})[/](\d{2})[/](\d{4})')
line_detail_re=re.compile(r'(\d+)[/](\d+) (\d+) (.*) (\d+) GBP Case (.*)[.](\d+) (.*)[.](\d+)')
#NLF Regular Expression compile
date_re=re.compile(r'Target on sale effective date (\d{2})[/](\d{2})[/](\d{4})')
VAT_20_re=re.compile(r'VAT Code 20.0 Standard')
VAT_0_re_1=re.compile(r'VAT Code Non')
VAT_0_re_2=re.compile(r'VAT Code 0.00')
case_size_re=re.compile(r'Case Size (\d+) ')
case_cost_re=re.compile(r'SKU Case Cost (.*)[.](.*) Layers')
prod_number_re=re.compile(r'SKU Number (\d+) ')
category_re=re.compile(r'Category (.*) Buyer')


def sainos_cpc_extract(file):
    VAT=None
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            if text==None:continue
            for line in text.split('\n'):
                line=" ".join(line.split())
                effective=effective_date_re.search(line)
                line_detail=line_detail_re.search(line)
                category=category_re.search(line)
                if effective:
                    Effective_Date=effective.group(1)+"/"+effective.group(2)+"/"+effective.group(3)
                elif line_detail:
                    Product_No=line_detail.group(3)
                    std_case_size=line_detail.group(5)
                    std_case_cost=line_detail.group(8)+"."+line_detail.group(9)
                    current_cost=line_detail.group(6)+"."+line_detail.group(7)
                    lines.append(Line(Product_No,Effective_Date,std_case_size,current_cost,std_case_cost,VAT))
                elif category:
                    if category.group(1)=="BWS":
                        VAT=20
                    else:
                        print("category error")
                        break


def sainos_nlf_extract(file):
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            if text==None:continue
            for line in text.split('\n'):
                line=" ".join(line.split())
                date=date_re.search(line)
                VAT20=VAT_20_re.search(line)
                VAT0=VAT_0_re_1.search(line)
                VAT0_2=VAT_0_re_2.search(line)
                case_size=case_size_re.search(line)
                case_cost=case_cost_re.search(line)
                prod_number=prod_number_re.search(line)
                if VAT20:
                    VAT=20
                elif VAT0:
                    VAT=0
                elif VAT0_2:
                    VAT=0
                elif case_size:
                    std_case_size=case_size.group(1)
                elif case_cost:
                    current_cost=None
                    std_case_cost=case_cost.group(1)+"."+case_cost.group(2)
                    std_case_cost=std_case_cost.replace(",","")
                elif prod_number:
                    Product_No=prod_number.group(1)
                elif date:
                    Effective_Date=date.group(1)+"/"+date.group(2)+"/"+date.group(3)
                    lines.append(Line(Product_No,Effective_Date,std_case_size,current_cost,std_case_cost,VAT))

def data_extraction(path1,path2):
    for filename in listdir_nohidden(path1):
        sainos_cpc_extract(os.path.join(path1,filename))
    for filename in listdir_nohidden(path2):
        sainos_nlf_extract(os.path.join(path2,filename))

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

def into_data_frame(lines):
    df=pd.DataFrame(lines)
    df.to_csv('CPC.csv',index=True)

data_extraction(cpc_from_path,nlf_from_path)
into_data_frame(lines)
