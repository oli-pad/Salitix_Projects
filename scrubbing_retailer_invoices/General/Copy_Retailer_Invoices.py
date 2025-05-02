import os
import shutil
import importlib.util
import pyodbc
from sys import argv
from Defining_Retailer import Defining_Retailer

# Dynamically import the logger_utils module
logger_utils_path = r"C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\logger_utils.py"
spec = importlib.util.spec_from_file_location("logger_utils", logger_utils_path)
logger_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logger_utils)

# Configure logging
MASTER_DB_CONN_STR = r'DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers'
SCRUBBED_DB_CONN_STR = r'DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Scrubbed_Data_Formatted;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers'
logger = logger_utils.setup_database_logger(MASTER_DB_CONN_STR, __name__)

# Define base paths
audit_base_path = r"W:\Audit"
invoice_image_folder_pattern = os.path.join(audit_base_path, "{}\\Invoice Images")
invoice_image_path_pattern = os.path.join(audit_base_path, "{}\\Invoice Images\\{}")
image_staging_bay = "ImageStagingBay"
scrubbed_charges_table = "[Salitix_Scrubbed_Data_Formatted].[dbo].[Scrubbed_Customer_Charges_Ftd]"

script, client_input = argv

def get_existing_invoices(connection_string):
    """Fetches a set of existing invoice filenames from the scrubbed data table."""
    existing_invoices = set()
    try:
        cnxn = pyodbc.connect(connection_string)
        cursor = cnxn.cursor()
        cursor.execute(f"SELECT DISTINCT Invoice_No FROM {scrubbed_charges_table}")
        for row in cursor:
            if row[0]:  # Ensure the filename is not None
                existing_invoices.add(row[0].lower())  # Convert to lowercase for case-insensitive comparison
        logger.info(f"Successfully retrieved {len(existing_invoices)} existing invoice filenames from {scrubbed_charges_table}.")
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logger.error(f"Error retrieving existing invoices from the database (SQLSTATE: {sqlstate}): {ex}")
    finally:
        if cnxn:
            cnxn.close()
    return existing_invoices

try:
    existing_invoices_in_db = get_existing_invoices(SCRUBBED_DB_CONN_STR)

    # List of things in the Audit folder.
    all_items_in_audit = os.listdir(audit_base_path)

    # Folders with Invoice Images
    audit_folders = [
        item
        for item in all_items_in_audit
        if os.path.exists(invoice_image_folder_pattern.format(item))
    ]

    if client_input == 'manual':
        # User input
        print("Available clients:", audit_folders)
        client_input = input("Please select a client from above or type 'all': ").strip()
        while client_input != "all" and client_input not in audit_folders:
            client_input = input("Invalid selection. Please select a client from above or type 'all': ").strip()

    if client_input == 'all':
        if 'Export com' in audit_folders:
            audit_folders.remove('Export com')
        clients_to_process = audit_folders
    else:
        clients_to_process = [client_input]

    for client in clients_to_process:
        logger.info(f"Starting processing for client: {client}")
        image_folder = invoice_image_folder_pattern.format(client)
        try:
            image_files = [item for item in os.listdir(image_folder) if item.lower().endswith(".pdf")]
            if not image_files:
                logger.info(f"No PDF files found in {image_folder} for client {client}.")
                continue

            for image_file in image_files:
                source_path = invoice_image_path_pattern.format(client, image_file)
                invoice_filename_lower = image_file.replace(".pdf", "").lower()
                if invoice_filename_lower not in existing_invoices_in_db:
                    try:
                        retailer = Defining_Retailer(source_path)
                        if retailer:
                            destination_folder = os.path.join(image_folder, image_staging_bay, retailer)
                            os.makedirs(destination_folder, exist_ok=True)
                            destination_path = os.path.join(destination_folder, image_file)
                            shutil.copy(source_path, destination_path)
                            logger.info(f"Copied new invoice '{image_file}' for client '{client}' to '{retailer}' ImageStagingBay.")
                        else:
                            logger.warning(f"Could not define retailer for new invoice '{image_file}' in client '{client}'. Skipping copy.")
                    except Exception as e:
                        logger.error(f"An error occurred while processing new invoice '{image_file}' for client '{client}': {e}")
                else:
                    logger.info(f"Invoice '{image_file}' for client '{client}' already exists in {scrubbed_charges_table}. Skipping copy.")
        except FileNotFoundError:
            logger.error(f"Invoice image folder not found for client: {client} at {image_folder}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing client '{client}': {e}")
        finally:
            logger.info(f"Finished processing for client: {client}.")

except Exception as e:
    logger.critical(f"An unhandled error occurred in the main part of the script: {e}")