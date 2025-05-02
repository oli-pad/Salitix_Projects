import pyodbc
import sys
import importlib.util

# Dynamically import the logger_utils module
logger_utils_path = r"C:\Users\python\Desktop\projects\scrubbing_retailer_invoices\logger_utils.py"
spec = importlib.util.spec_from_file_location("logger_utils", logger_utils_path)
logger_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logger_utils)

# Configure logging
MASTER_DB_CONN_STR = r'DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers'
logger = logger_utils.setup_database_logger(MASTER_DB_CONN_STR, __name__)

# Path: scrubbing_retailer_invoices/General/Run_Format_Procedure.py

Client_code_dic = {
    'Ab_Inbev': "CL023", 'AG_Barr': "CL005", 'Bacardi': "CL001",
    'Burtons': "CL003", 'Coty': "CL027", 'Finsbury_Foods': "CL014",
    'Foxs': "CL999", 'Heineken': "CL028", 'Kettle Foods': "CL026",
    'Kinnerton': "CL022", 'Maxxium': "CL012", 'Pladis': "CL002",
    'Premier_Foods': "CL020", 'Princes': "CL029", 'Tilda': "CL013", 'Youngs': "CL004",
    'Loreal': 'CL031'
}
Retailer_Code_dic = {'Tesco': "TES01", 'ASDA': "ASD01", 'Sainsburys': "SAI01", 'Morrisons': "MOR01"}

def main(client_arg, retailer_arg):
    """Runs the stored procedure prc_Run_SCC_Load_Scrubbed_Customer_Charges_DTL."""
    logger.info(f"Starting Run_Format_Procedure for Client: {client_arg}, Retailer: {retailer_arg}")

    if client_arg not in Client_code_dic:
        logger.error(f"Invalid Client Code: {client_arg}")
        return
    if retailer_arg not in Retailer_Code_dic:
        logger.error(f"Invalid Retailer Code: {retailer_arg}")
        return

    Salitix_Client_Number = Client_code_dic[client_arg]
    Salitix_Customer_Number = Retailer_Code_dic[retailer_arg]

    conn_str = r'DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers'
    conn = None  # Initialize conn outside the try block
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        sql_query = f"EXEC [Salitix_Master_Data].[dbo].[prc_Run_SCC_Load_Scrubbed_Customer_Charges_DTL] ?, ?"
        logger.info(f"Executing SQL Query: {sql_query} with parameters: ({Salitix_Client_Number}, {Salitix_Customer_Number})")
        cursor.execute(sql_query, Salitix_Client_Number, Salitix_Customer_Number)
        conn.commit()
        logger.info(f"Successfully executed stored procedure for Client: {client_arg}, Retailer: {retailer_arg}")

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logger.error(f"Database error occurred: {ex}")
        if conn:
            conn.rollback()
            logger.warning("Transaction rolled back due to error.")
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.error("Usage: python Run_Format_Procedure.py <client> <retailer>")
        sys.exit(1)
    client = sys.argv[1]
    retailer = sys.argv[2]
    main(client, retailer)