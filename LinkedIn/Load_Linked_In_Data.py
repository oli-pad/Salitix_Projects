import pyodbc
import pandas as pd
import os

#connect to database
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Sandbox;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers')
cursor = conn.cursor()

#store the table in a dataframe
sqlcommand = "SELECT * FROM [Sandbox].[dbo].[Salitix_LinkedIn_interaction]"
Salitix_LinkedIn_interaction_df = pd.read_sql(sqlcommand,conn)

Month = input("Enter the month: ")
Year = input("Enter the year: ")

#function to insert data into database
def insert_into_staging(df,filename):
    sqlcommand = "INSERT INTO [Sandbox].[dbo].[Salitix_LinkedIn_interaction] (id,first_name,last_name,profile_link,job_title " \
      ",company_name,email,phone,address,image_link,follower_count,tags,contact_status,conversation_status,object_urn" \
      ",public_identifier,profile_link_public_identifier,thread,invited_at,connected_at,company_universal_name,company_website" \
      ",employee_count_start,employee_count_end,industries,location,imported_profile_link,name,Story_Name,month,year)" \
      " VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}',{},'{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}');"
    for x,row in df.iterrows():
        row = [str(j).replace("'","") for j in row]
        row = [str(j).replace('"',"") for j in row]
        row = [str(j).replace("nan","") for j in row]
        row = [str(j).replace("None","") for j in row]
        row = [str(j).replace("  "," ") for j in row]
        row[19] = row[19][:10]
        if row[19]=='':row[19]='NULL'
        filename = filename.replace("'","")
        if not check_if_row_exists(row,filename):
            cursor.execute(sqlcommand.format(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]
                                            ,row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15]
                                            ,row[16],'',row[18],row[19],row[20],row[21],row[22],row[23]
                                            ,row[24],row[25],row[26],row[27],filename.replace(".csv",""),Month,Year))
            cursor.commit()

def read_excel_file(file):
    df=pd.read_csv(os.path.join(r"W:\Admin\Client Engagement Trackers\Linkedin_Expandi_Files",file))
    print(df)
    insert_into_staging(df,file)

def check_if_row_exists(row,filename):
    #if row in the df then retrun false
    id_list= Salitix_LinkedIn_interaction_df["id"].unique()
    id_list = [str(i.replace(" ","")) for i in id_list]
    story_name_list = Salitix_LinkedIn_interaction_df["Story_Name"].unique()
    print(story_name_list)
    if row[0] in id_list and filename.replace(".csv","") in story_name_list:
        return True
    else:
        return False
    

#List of files in the Audit folder.
directory_list = [ item for item in os.listdir(r"W:\Admin\Client Engagement Trackers\Linkedin_Expandi_Files") if ".csv" in item]

for i in directory_list:
    read_excel_file(i)