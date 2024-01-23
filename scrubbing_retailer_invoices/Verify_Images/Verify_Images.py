import os
import pdfplumber
import re
import os

dict= {
'Ab Inbev':['018245','3000002672'],
'AG Barr':['010566','1000048','20889','3000000484'],
'Bacardi':["3000000338","018112","230073","1000033"],
'Burtons':['011091','20933','3000003655'],
'Coty':['069203','2017482','30598','3000005959','20911'],
'Finsbury_Foods':['837701','1001939','120620','130691','3000001161'],
'Heineken':['018260','1002529','190716','3000000404'],
'Kettle Foods':['811654','110035','3000000970'],
'Kinnerton':[],
'Loreal':['044175','1001794','70250','3000002717'],
'Maxxium':['019912','1001738','70564','3000000297'],
'Pladis':['012172','1002917','1002917','3000002825'],
'Premier Foods':['010364','1001986','130587','160819','3000000324'],
'Princes':[''],
'Tilda':[],
'Youngs':[],
}

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def move_file(source_path, destination_path):
    if os.path.exists(destination_path):
        os.remove(destination_path)
    os.rename(source_path, destination_path)

def ConvertPDFtoText(file):
    pdf_text=''
    with pdfplumber.open(file) as pdf:
        pages=pdf.pages
        for page in pdf.pages:
            text=page.extract_text()
            pdf_text+=text
    return pdf_text

def get_Client_Number(file):
    pdf_text=ConvertPDFtoText(file)
    for line in pdf_text.split('\n'):
        if re.search(r'Customer(\s?)No(\s?):(\s?)(\d+)',line):
            client_number=re.search(r'Customer(\s?)No(\s?):(\s?)(\d+)',line).group(4)
            return client_number
        if re.search(r'ASDA(\s?)Supplier(\s?)Number(\s?)(\d+)',line):
            client_number=re.search(r'ASDA(\s?)Supplier(\s?)Number(\s?)(\d+)',line).group(4)
            return client_number
        if re.search(r'Supplier(\s?)ID(\s?):(\s?)(\d+)',line):
            client_number=re.search(r'Supplier(\s?)ID(\s?):(\s?)(\d+)',line).group(4)
            return client_number

def main(folder_path):
    for file in os.listdir(folder_path):
        if not file.endswith('.pdf'):
            continue
        print(file)
        path_components = folder_path.split('\\')
        client_number = get_Client_Number(os.path.join(folder_path,file))
        if client_number in dict[path_components[2]]:
            continue
        else:    
            create_folder_if_not_exists(os.path.join(folder_path,"Incorrect"))
            move_file(os.path.join(folder_path,file),os.path.join(os.path.join(folder_path,"Incorrect"),file))

def remove_files_with_same_name(source_folder, destination_folder):
    for file in os.listdir(source_folder):
        destination_file_path = os.path.join(destination_folder, file)
        if os.path.isfile(destination_file_path):
            os.remove(destination_file_path)




main(r'W:\Audit\Pladis\Invoice Images\ImageStagingBay\Morrisons')