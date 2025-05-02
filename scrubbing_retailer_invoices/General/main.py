#This file will feed from the flask form

# Path: scrubbing_retailer_invoices/General/main.py

import sys
from datetime import datetime
import importlib.util
import subprocess


script, process, client, retailer, start_date, end_date = sys.argv

print("Process: ", process, " Client: ", client, " Retailer: ", retailer)

# Dynamically import the logger_utils module
logger_utils_path = r"C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\logger_utils.py"
spec = importlib.util.spec_from_file_location("logger_utils", logger_utils_path)
logger_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logger_utils)

# Configure logging
MASTER_DB_CONN_STR = r'DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers'
logger = logger_utils.setup_database_logger(MASTER_DB_CONN_STR, __name__)


# Harvesting
Harvesting_format = r"python C:\Users\python\Desktop\projects\Invoice_Harvesting\General\Harvesting.py {} {}"
# Rename
Rename_format = r"python C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\General\Rename_Invoices.py {}"
# Copy
Copy_format = r"python C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\General\Copy_Retailer_Invoices.py {}"
# Scrubbing
Scrubbing_format = r'python C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\General\Scrubbing_all_Invoices.py "{}" "{}"'
# Scraping
Scraping_format = r"python C:\Users\python\Desktop\projects\web_portal_scraping\ASDA_Retail_Link\Repeating_Code.py {} {}"
# Loading
Loading_format = r"python C:\Users\python\Desktop\projects\Excel_Customer_Charges\ASDA_Excel_Customer_Charges.py {}"
# Transfer
Transfer_format = r"python C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\General\Run_Format_Procedure.py"
# Run the Identify Client Number
Identify_Client_format = r"python C:\Users\python\Desktop\IdentifyingInvoiceClientNumber\main.py"
# Update_Header
Update_Header_format = r"python C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\Updating_Hdr\Updating_Hdr_of_Ftd.py {} {}"
# Load into
Load_into_format = r"python C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\General\IA_Procedure.py {} {}"

client_list = [client]
if retailer == "All":
    retailer_list = ["ASDA", "Sainsburys", "Tesco", "Morrisons"]
    logger.info(f"Retailer List: {retailer_list}")
else:
    retailer_list = [retailer]
    logger.info(f"Processing for Retailer: {retailer}")

def run_subprocess(command):
    """Executes a subprocess and logs the output and errors."""
    logger.info(f"Executing command: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        logger.info(f"Command '{command}' completed successfully.")
        if result.stdout:
            logger.debug(f"Stdout: {result.stdout.strip()}")
        if result.stderr:
            logger.debug(f"Stderr: {result.stderr.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command '{command}' failed with error: {e}")
        if e.stdout:
            logger.error(f"Stdout: {e.stdout.strip()}")
        if e.stderr:
            logger.error(f"Stderr: {e.stderr.strip()}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while running '{command}': {e}")
        return False

if process == "All":
    logger.info("Starting 'All' process.")
    run_subprocess(Harvesting_format.format(client_list[0], retailer))
    logger.info("Harvesting Done")
    run_subprocess(Rename_format.format(client_list[0]))
    logger.info("Renaming Done")
    run_subprocess(Copy_format.format(client_list[0]))
    logger.info("Copying Done")
    run_subprocess(Scrubbing_format.format(client_list[0], retailer_list))
    logger.info("Scrubbing Done")
    if "ASDA" in retailer_list:
        logger.info("Starting ASDA Scraping and Loading.")
        run_subprocess(Scraping_format.format(start_date, end_date))
        logger.info("ASDA Scraping Done")
        run_subprocess(Loading_format.format(client_list[0]))
        logger.info("ASDA Loading Done")
    run_subprocess(Transfer_format)
    logger.info("Transfer Done")
    run_subprocess(Identify_Client_format)
    logger.info("Identifying Client Number Done")
    logger.info("Checking for any incorrect images (manual step, no automation here).")
    logger.info("Starting Second Stage Scrubbing.")
    for i in retailer_list:
        run_subprocess(Update_Header_format.format(client_list[0], i))
    logger.info("Header Update Done")
    for r in retailer_list:
        run_subprocess(Load_into_format.format(client_list[0], r))
    logger.info("Load into IA Procedure Done")
    logger.info("All processes in 'All' completed.")
elif process == "Harvest":
    logger.info("Starting Harvesting.")
    run_subprocess(Harvesting_format.format(client_list[0], retailer))
    logger.info("Harvesting Done")
elif process == "Rename":
    logger.info("Starting Renaming.")
    run_subprocess(Rename_format.format(client_list[0]))
    logger.info("Renaming Done")
elif process == "Copy":
    logger.info("Starting Copying.")
    run_subprocess(Copy_format.format(client_list[0]))
    logger.info("Copying Done")
elif process == "Scrub":
    logger.info("Starting Scrubbing.")
    run_subprocess(Scrubbing_format.format(client_list[0], retailer_list))
    logger.info("Scrubbing Done")
elif process == "ASDA only : Scraping":
    logger.info("Starting ASDA Scraping.")
    run_subprocess(Scraping_format.format(start_date, end_date))
    logger.info("ASDA Scraping Done")
elif process == "ASDA only : Load":
    logger.info("Starting ASDA Loading.")
    run_subprocess(Loading_format.format(client_list[0]))
    logger.info("ASDA Loading Done")
elif process == "Transfer to Ftd table":
    logger.info("Starting Transfer to Ftd table.")
    run_subprocess(Transfer_format)
    logger.info("Transfer Done")
    run_subprocess(Identify_Client_format)
    logger.info("Identifying Client Number Done")
else:
    logger.warning(f"Invalid Process: '{process}'.")