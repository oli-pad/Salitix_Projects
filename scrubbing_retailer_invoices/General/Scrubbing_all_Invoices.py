import os
import pyodbc
import pandas as pd
from sys import argv
import sys
import importlib.util

# Dynamically import the logger_utils module
logger_utils_path = r"C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\logger_utils.py"
spec = importlib.util.spec_from_file_location("logger_utils", logger_utils_path)
logger_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logger_utils)

# Configure logging
MASTER_DB_CONN_STR = r'DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers'
SCRUBBED_STG_DB_CONN_STR = r'DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Scrubbed_Data_Staging;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers'
logger = logger_utils.setup_database_logger(MASTER_DB_CONN_STR, __name__)

script, client_input, customer_input = argv

CLIENT_CODE_MAPPING = {
    'Ab_Inbev': "CL023", 'AG_Barr': "CL005", 'Bacardi': "CL001",
    'Burtons': "CL003", 'Coty': "CL027", 'Finsbury_Foods': "CL014",
    'Foxs': "CL999", 'Heineken': "CL028", 'Kettle Foods': "CL026",
    'Kinnerton': "CL022", 'Maxxium': "CL012", 'Pladis': "CL002",
    'Premier_Foods': "CL020", 'Princes': "CL029", 'Tilda': "CL013", 'Youngs': "CL004",
    'Loreal': 'CL031'
}

RETAILER_MAPPING = {
    "Tesco": ("TES01", "No", "Tesco", "Tesco_Invoice_Scrubbing", "data_extraction_Tesco"),
    "Morrisons": ("MOR01", "No", "Morrisons", "Morrisons_Invoice_Scrubbing", "data_extraction_morrisons"),
    "Sainsbury": ("SAI01", "No", "Sainsbury", "Sainsbury_Invoice_Scrubbing", "data_extraction_Sainsburys"),
    "ASDA": ("ASD01", "Yes", "ASDA", "ASDA_Invoice_Scrubbing", "data_extraction_ASDA")
}

AUDIT_BASE_PATH = r"W:\Audit"
INVOICE_IMAGE_FOLDER_PATTERN = os.path.join(AUDIT_BASE_PATH, "{}\\Invoice Images")
INVOICE_IMAGE_STAGING_PATH = os.path.join(AUDIT_BASE_PATH, "{}\\Invoice Images\\ImageStagingBay\\{}")
SCRUBBED_STAGING_TABLE = "[Salitix_Scrubbed_Data_Staging].[dbo].[Scrubbed_Customer_Charges_Stg]"
SCRUBBED_ASDA_STAGING_TABLE = "[Salitix_Scrubbed_Data_Staging].[dbo].[Scrubbed_ASDA_Customer_Charges_Stg]"
SCRUBBING_MODULE_BASE_PATH = r'C:\Users\python\Desktop\projects\scrubbing_retailer_invoices'

def clear_staging_tables(connection_string):
    """Deletes all records from the staging tables."""
    try:
        cnxn = pyodbc.connect(connection_string)
        cursor = cnxn.cursor()
        cursor.execute(f"DELETE FROM {SCRUBBED_STAGING_TABLE}")
        cursor.execute(f"DELETE FROM {SCRUBBED_ASDA_STAGING_TABLE}")
        cursor.commit()
        logger.info("Successfully cleared the staging tables.")
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logger.error(f"Error clearing staging tables (SQLSTATE: {sqlstate}): {ex}")
        if cnxn:
            cnxn.rollback()
    finally:
        if cnxn:
            cnxn.close()

def insert_into_staging(df, client_code, retailer_code, is_asda):
    """Inserts data from a DataFrame into the appropriate staging table."""
    df_columns = [str(i).replace(" ", "_") for i in df.columns.tolist()]
    cols = ",".join(df_columns)
    table_name = SCRUBBED_ASDA_STAGING_TABLE if is_asda == "Yes" else SCRUBBED_STAGING_TABLE
    insert_sql_template = f"INSERT INTO {table_name} ({cols}) VALUES ({','.join(['?'] * len(df_columns))})"

    try:
        cnxn = pyodbc.connect(SCRUBBED_STG_DB_CONN_STR)
        cursor = cnxn.cursor()
        for _, row in df.iterrows():
            row_values = [str(j).replace("'", "") if pd.notna(j) else "NULL" for j in row]

            # Apply transformations
            row_values[0] = client_code
            row_values[1] = retailer_code
            for idx in [8, 11, 12]:
                if row_values[idx] != "NULL" and len(row_values[idx]) == 8 and row_values[idx].isdigit():
                    row_values[idx] = f"{row_values[idx][6:]}-{row_values[idx][3:5]}-{row_values[idx][:2]}"

            for idx in range(13, 18):
                try:
                    row_values[idx] = str(round(float(row_values[idx]), 2)) if row_values[idx] != "NULL" else "NULL"
                except (ValueError, TypeError):
                    pass

            try:
                if row_values[16] != "NULL" and float(row_values[16]) > 1:
                    row_values[16] = str(float(row_values[16]) / 100)
            except (ValueError, TypeError):
                pass

            cursor.execute(insert_sql_template, row_values)
        cnxn.commit()
        logger.info(f"Successfully inserted {len(df)} rows into {table_name} for client {client_code} and retailer {retailer_code}.")
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logger.error(f"Error inserting data into {table_name} (SQLSTATE: {sqlstate}): {ex}")
        if cnxn:
            cnxn.rollback()
    finally:
        if cnxn:
            cnxn.close()

def process_client_retailer(client, customer):
    """Processes data extraction and insertion for a given client and retailer."""
    if client not in CLIENT_CODE_MAPPING:
        logger.error(f"Client '{client}' not found in CLIENT_CODE_MAPPING.")
        return

    if customer not in RETAILER_MAPPING:
        logger.warning(f"Retailer '{customer}' not found in RETAILER_MAPPING. Skipping.")
        return

    retailer_code, is_asda, retailer_folder_name, module_name, function_name = RETAILER_MAPPING[customer]
    client_code = CLIENT_CODE_MAPPING[client]
    image_folder = INVOICE_IMAGE_STAGING_PATH.format(client, retailer_folder_name)
    module_path = os.path.join(SCRUBBING_MODULE_BASE_PATH, retailer_folder_name)
    sys.path.insert(0, module_path)

    try:
        module = __import__(module_name)
        extraction_function = getattr(module, function_name)
        df = extraction_function(image_folder)
        insert_into_staging(df, client_code, retailer_code, is_asda)
    except ImportError as e:
        logger.error(f"Error importing module '{module_name}': {e}")
    except AttributeError as e:
        logger.error(f"Error accessing function '{function_name}' in module '{module_name}': {e}")
    except Exception as e:
        logger.error(f"An error occurred during data extraction or insertion for {client} - {customer}: {e}")
    finally:
        if module_path in sys.path:
            sys.path.remove(module_path)

if __name__ == "__main__":
    clear_staging_tables(SCRUBBED_STG_DB_CONN_STR)

    directory_list = os.listdir(AUDIT_BASE_PATH)
    audit_folder_list = [item for item in directory_list if os.path.exists(INVOICE_IMAGE_FOLDER_PATTERN.format(item))]

    clients_to_process = []
    if client_input == 'manual':
        print("Available clients:", audit_folder_list)
        client_input = input("Please select a client from above or type 'all': ").strip()
        while client_input != "all" and client_input not in audit_folder_list:
            client_input = input("Invalid selection. Please select a client from above or type 'all': ").strip()

    if client_input == 'all':
        clients_to_process = [c for c in audit_folder_list if c != 'Export com']
        logger.info(f"Processing all clients: {clients_to_process}")
    else:
        clients_to_process = [client_input]
        logger.info(f"Processing client: {clients_to_process}")

    retailers_to_process =  [cust.replace('[','').replace(']','').replace("'","") for cust in customer_input.split(',')]
    logger.info(f"Processing retailers: {retailers_to_process}")

    for client in clients_to_process:
        for retailer in retailers_to_process:
            process_client_retailer(client, retailer)

    logger.info("Script execution completed.")