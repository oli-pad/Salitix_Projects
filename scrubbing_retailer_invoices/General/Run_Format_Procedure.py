import importlib.util
import pyodbc

# Dynamically import the logger_utils module
logger_utils_path = r"C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\logger_utils.py"
spec = importlib.util.spec_from_file_location("logger_utils", logger_utils_path)
logger_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logger_utils)

# Configure logging
MASTER_DB_CONN_STR = r'DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers'
logger = logger_utils.setup_database_logger(MASTER_DB_CONN_STR, __name__)

# Path: scrubbing_retailer_invoices/General/Run_Format_Procedure.py

def run_format_procedure():
    """
    Connects to the Salitix Master Data database and executes the
    Format_Scrubbed_Charges stored procedure, logging the process.
    """
    conn = None  # Initialize conn to None for proper finally block handling
    try:
        conn_str = 'DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        sql_query = "EXEC [Salitix_Scrubbed_Data_Formatted].[dbo].[Format_Scrubbed_Charges]"
        logger.info('Running "EXEC [Salitix_Scrubbed_Data_Formatted].[dbo].[Format_Scrubbed_Charges]"')
        cursor.execute(sql_query)
        conn.commit()
        logger.info("Stored procedure 'Format_Scrubbed_Charges' executed successfully.")

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logger.error(f"Error executing stored procedure (SQLSTATE: {sqlstate}): {ex}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    run_format_procedure()