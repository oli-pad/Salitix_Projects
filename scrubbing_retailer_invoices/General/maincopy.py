import sys
import subprocess
import importlib.util

# Dynamically import the logger_utils module
logger_utils_path = r"C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\logger_utils.py"
spec = importlib.util.spec_from_file_location("logger_utils", logger_utils_path)
logger_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logger_utils)

# Configure logging
MASTER_DB_CONN_STR = 'DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers'
logger = logger_utils.setup_database_logger(MASTER_DB_CONN_STR, __name__)

# Script paths
UPDATE_HEADER_SCRIPT = r"C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\Updating_Hdr\Updating_Hdr_of_Ftd.py"
LOAD_INTO_IA_SCRIPT = r"C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\General\IA_Procedure.py"

import subprocess

def run_script(script_path, client, retailer):
    """Runs a Python script using subprocess and logs the result."""
    try:
        # Explicitly specify the virtual environment's Python interpreter
        python_executable = sys.executable #this gets the path to the current python interpreter.
        command = [python_executable, script_path, client, retailer]
        logger.info(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info(f"Script '{script_path}' for client '{client}' and retailer '{retailer}' completed successfully.")
        if result.stdout:
            logger.info(f"Script output: {result.stdout}")
        if result.stderr:
            if "SyntaxWarning" in result.stderr:
                logger.warning(f"Script warning output: {result.stderr}")
            else:
                logger.error(f"Script error output: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running script '{script_path}' for client '{client}' and retailer '{retailer}': {e}")
        if e.stderr:
            logger.error(f"Script stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.exception(f"An unexpected error occurred running '{script_path}' for '{client}' and '{retailer}'")
        return False

def main(process, client, retailer):
    """Main function to execute the specified process."""
    logger.info(f"Starting process: {process}, Client: {client}, Retailer: {retailer}")

    client_list = [client]
    retailer_list = ["ASDA", "Sainsbury", "Tesco", "Morrisons"] if retailer == "All" else [retailer]

    if process == "All":
        all_update_success = True
        for retailer_item in retailer_list:
            if not run_script(UPDATE_HEADER_SCRIPT, client_list[0], retailer_item):
                all_update_success = False
        if all_update_success:
            logger.info("All 'Update Header' processes completed successfully.")
        else:
            logger.error("One or More 'Update Header' processes failed.")

        all_load_success = True
        for retailer_item in retailer_list:
            if not run_script(LOAD_INTO_IA_SCRIPT, client_list[0], retailer_item):
                all_load_success = False
        if all_load_success:
            logger.info("All 'Load into IA Procedure' processes completed successfully.")
        else:
            logger.error("One or more 'Load into IA Procedure' processes failed.")

        if all_update_success and all_load_success:
            logger.info("All processes completed successfully.")
        else:
            logger.error("One or more processes failed.")

    elif process == "Update HDR Column":
        all_update_success = True
        for retailer_item in retailer_list:
            if not run_script(UPDATE_HEADER_SCRIPT, client_list[0], retailer_item):
                all_update_success = False
        if all_update_success:
            logger.info("'Update Header' process completed successfully.")
        else:
            logger.error("'Update Header' process failed.")

    elif process == "Load into IA Procedure":
        all_load_success = True
        for retailer_item in retailer_list:
            if not run_script(LOAD_INTO_IA_SCRIPT, client_list[0], retailer_item):
                all_load_success = False
        if all_load_success:
            logger.info("'Load into IA Procedure' process completed successfully.")
        else:
            logger.error("'Load into IA Procedure' process failed.")
    else:
        logger.error("Invalid Process Contact OO for help.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        logger.error("Usage: python main.py <process> <client> <retailer>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])