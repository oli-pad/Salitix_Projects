import pyodbc
import pandas as pd
import sys
import logging
import datetime
import time

# Configuration dictionaries
CLIENT_CODE_MAP = {
    'Ab_Inbev': "CL023", 'AG_Barr': "CL005", 'Bacardi': "CL001",
    'Burtons': "CL003", 'Coty': "CL027", 'Finsbury_Foods': "CL014",
    'Foxs': "CL999", 'Heineken': "CL028", 'Kettle Foods': "CL026",
    'Kinnerton': "CL022", 'Maxxium': "CL012", 'Pladis': "CL002",
    'Premier_Foods': "CL020", 'Princes': "CL029", 'Tilda': "CL013", 'Youngs': "CL004",
    'Loreal': 'CL031'
}

RETAILER_CODE_MAP = {
    'Tesco': "TES01", 'ASDA': "ASD01", 'Sainsbury': "SAI01", 'Morrisons': "MOR01"
}

# Database connection strings
MASTER_DB_CONN_STR = r'DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Master_Data;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers'
SCRUBBED_DB_CONN_STR = r'DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE=Salitix_Scrubbed_Data_Formatted;Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers'

class DatabaseHandler(logging.Handler):
    """
    Custom logging handler to insert log messages into a database table.
    """
    def __init__(self, connection_string):
        super().__init__()
        self.connection_string = connection_string
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s - %(module)s - %(funcName)s')

    def emit(self, record):
        try:
            formatted_record = self.formatter.format(record)
            with pyodbc.connect(self.connection_string, autocommit=True) as conn:
                cursor = conn.cursor()
                dt_object = datetime.datetime.fromtimestamp(record.created)
                dt_string = dt_object.isoformat()  # Convert to ISO 8601 string
                cursor.execute(
                    "INSERT INTO [Salitix_Master_Data].[dbo].[Salitix_Python_Log] ([timestamp], [level], [message], [module], [function]) VALUES (?, ?, ?, ?, ?)",
                    dt_string, record.levelname, record.message, record.module, record.funcName
                )
        except pyodbc.Error as e:
            # Important: Log to a file or standard error *outside* the database handler
            print(f"Database logging error: {e}")
            sys.stderr.write(f"Database logging error: {e}\n")

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set a default level

# Add the database handler
db_handler = DatabaseHandler(MASTER_DB_CONN_STR)
logger.addHandler(db_handler)

# Add a basic stream handler as a fallback (optional, but good for console output)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)  # Only log warnings and above to console by default
stream_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)


def get_client_db(client_code):
    """Retrieves the client database name from the master database."""
    try:
        with pyodbc.connect(MASTER_DB_CONN_STR) as conn:
            query = f"SELECT Db FROM [Salitix_Master_Data].[dbo].[salitix_client_numbers] WHERE Salitix_client_number='{client_code}';"
            result = pd.read_sql(query, conn)
            if not result.empty:
                db_name = result['Db'].iloc[0]
                logger.debug(f"Client database for code '{client_code}': {db_name}")
                return db_name
            else:
                logger.error(f"Client code '{client_code}' not found in master database.")
                return None
    except pyodbc.Error as e:
        sqlstate = e.args[0]
        logger.error(f"Database error retrieving client DB for code '{client_code}' (SQLSTATE: {sqlstate}): {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error retrieving client DB for code '{client_code}': {e}")
        return None



def get_hdr_invoices(client_db, retailer_code):
    """Retrieves HDR invoices from the client database."""
    client_conn_str = f'DRIVER=SQL Server;SERVER=UKSALAZSQL;DATABASE={client_db};Trusted_Connection=Yes;UID=SALITIX\SQLSalitixAuditorUsers'
    try:
        with pyodbc.connect(client_conn_str) as conn:
            query = f"SELECT Retailer_Invoice FROM [dbo].[vw_SAL_Customer_Charges_Alt] WHERE [Salitix_Customer_Number] = '{retailer_code}' AND [CC_DTL_ID] IS NULL"
            df = pd.read_sql(query, conn)
            invoices = df['Retailer_Invoice'].tolist()
            logger.debug(f"HDR Invoices for retailer '{retailer_code}': {invoices}")
            return invoices
    except pyodbc.Error as e:
        sqlstate = e.args[0]
        logger.error(f"Database error retrieving HDR invoices for retailer '{retailer_code}' from '{client_db}' (SQLSTATE: {sqlstate}): {e}")
        return []
    except Exception as e:
        logger.exception(f"Unexpected error retrieving HDR invoices for retailer '{retailer_code}' from '{client_db}': {e}")
        return []



def get_scrubbed_invoices(client_code, retailer_code):
    """Retrieves scrubbed invoices from the scrubbed formatted data."""
    try:
        with pyodbc.connect(SCRUBBED_DB_CONN_STR) as conn:
            query = f"SELECT Invoice_No FROM [dbo].[Scrubbed_Customer_Charges_Ftd] WHERE Salitix_customer_number='{retailer_code}' AND Salitix_client_number ='{client_code}' GROUP BY Invoice_No"
            df = pd.read_sql(query, conn)
            invoices = df['Invoice_No'].tolist()
            logger.debug(f"Scrubbed Invoices for client '{client_code}', retailer '{retailer_code}': {invoices}")
            return invoices
    except pyodbc.Error as e:
        sqlstate = e.args[0]
        logger.error(f"Database error retrieving scrubbed invoices for client '{client_code}', retailer '{retailer_code}' (SQLSTATE: {sqlstate}): {e}")
        return []
    except Exception as e:
        logger.exception(f"Unexpected error retrieving scrubbed invoices for client '{client_code}', retailer '{retailer_code}': {e}")
        return []



def get_all_scrubbed_data(client_code, retailer_code):
    """Retrieves all scrubbed data for the given client and retailer."""
    try:
        with pyodbc.connect(SCRUBBED_DB_CONN_STR) as conn:
            query = f"SELECT * FROM [dbo].[Scrubbed_Customer_Charges_Ftd] WHERE Salitix_customer_number='{retailer_code}' AND Salitix_client_number ='{client_code}'"
            df = pd.read_sql(query, conn)
            logger.debug(f"Retrieved all scrubbed data for client '{client_code}', retailer '{retailer_code}'.  Shape: {df.shape}")
            return df
    except pyodbc.Error as e:
        sqlstate = e.args[0]
        logger.error(f"Database error retrieving all scrubbed data for client '{client_code}', retailer '{retailer_code}' (SQLSTATE: {sqlstate}): {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.exception(f"Unexpected error retrieving all scrubbed data for client '{client_code}', retailer '{retailer_code}': {e}")
        return pd.DataFrame()



def update_hdr_invoice(hdr_no, inv_no):
    """Updates the HDR invoice number in the scrubbed formatted data."""
    try:
        with pyodbc.connect(SCRUBBED_DB_CONN_STR, autocommit=True) as conn:
            cursor = conn.cursor()
            query = f"UPDATE [dbo].[Scrubbed_Customer_Charges_Ftd] SET HDR_Invoice_Number = '{hdr_no}' WHERE Invoice_No = '{inv_no}';"
            cursor.execute(query)
            logger.info(f"Updated HDR invoice: {hdr_no} to Invoice: {inv_no}")
    except pyodbc.Error as e:
        sqlstate = e.args[0]
        logger.error(f"Database update error (SQLSTATE: {sqlstate}): {e}")
    except Exception as e:
        logger.exception(f"Unexpected error during HDR invoice update: {e}")



def process_invoices(hdr_list, cc_list, all_scrubbed_df, retailer_code, client_code):
    """Processes and updates invoices based on retailer and client codes."""
    processed_count = 0
    total_count = len(hdr_list)
    logger.info(f"Processing {total_count} HDR invoices for retailer: {retailer_code}, client: {client_code}")

    for hdr_invoice in hdr_list:
        if hdr_invoice in cc_list:
            logger.debug(f"HDR Invoice '{hdr_invoice}' already in CC list. Skipping.")
            continue

        updated = False # Flag to track if an update occurred

        if retailer_code == "TES01":
            prefixes = ["100", "1002", "10021", "1"]
            for prefix in prefixes:
                if prefix + hdr_invoice in cc_list:
                    update_hdr_invoice(hdr_invoice, prefix + hdr_invoice)
                    processed_count += 1
                    updated = True
                    break  # Exit the prefix loop
            if not updated:
                logger.debug(f"HDR Invoice '{hdr_invoice}' not found with TES01 prefixes.")

        elif retailer_code == "ASD01":
            if hdr_invoice[:10] in cc_list:
                update_hdr_invoice(hdr_invoice, hdr_invoice[:10])
                processed_count += 1
                updated = True
            elif hdr_invoice.replace("P-", "") in cc_list:
                update_hdr_invoice(hdr_invoice, hdr_invoice.replace("P-", ""))
                processed_count += 1
                updated = True
            if not updated:
                logger.debug(f"HDR Invoice '{hdr_invoice}' not found with ASD01 rules.")

        elif retailer_code == "SAI01":
            replacements = [
                (" _ ", "-"), (" _ ", "_"), ("/", "_"), ("/", ""), ("-", "_"), ("-", " _ ")
            ]
            for old, new in replacements:
                modified_invoice = hdr_invoice.replace(old, new)
                if modified_invoice in cc_list:
                    update_hdr_invoice(hdr_invoice, modified_invoice)
                    processed_count += 1
                    updated = True
                    break # Exit replacement loop
            if not updated:
                logger.debug(f"HDR Invoice '{hdr_invoice}' not found with SAI01 replacements.")

        if client_code == 'CL029':
            modified_invoice = "RP" + hdr_invoice.replace("/", "_P0175_")
            if modified_invoice in cc_list:
                update_hdr_invoice(hdr_invoice, modified_invoice)
                processed_count += 1
                updated = True
            if not updated and client_code == 'CL029':
                logger.debug(f"HDR Invoice '{hdr_invoice}' not found with CL029 rule.")

        elif client_code == 'CL020':
            replacements_client = ["_P0819_", "_M0587_"]
            for rep in replacements_client:
                modified_invoice = hdr_invoice.replace("/", rep)
                if modified_invoice in cc_list:
                    update_hdr_invoice(hdr_invoice, modified_invoice)
                    processed_count += 1
                    updated = True
                    break
            if not updated and client_code == 'CL020':
                logger.debug(f"HDR Invoice '{hdr_invoice}' not found with CL020 rules.")

        elif retailer_code == "MOR01":
            years = [str(year) for year in range(2017, 2027)]
            for year in years:
                if year + hdr_invoice[4:] in cc_list:
                    update_hdr_invoice(hdr_invoice, year + hdr_invoice[4:])
                    processed_count += 1
                    updated = True
                    break
                if year + hdr_invoice in cc_list:
                    update_hdr_invoice(hdr_invoice, year + hdr_invoice)
                    processed_count += 1
                    updated = True
                    break
            if not updated:
                if hdr_invoice.replace("_", "") in cc_list:
                    update_hdr_invoice(hdr_invoice, hdr_invoice.replace("_", ""))
                    processed_count += 1
                    updated = True
                elif "DEAL" in hdr_invoice or "." in hdr_invoice:
                    deal_no = hdr_invoice.replace("DEAL", "")
                    string_split = deal_no.split()
                    promotion_no = string_split[0]
                    if len(hdr_invoice) > 10:
                        date = hdr_invoice[-8:]
                        invoice_date = date[:2] + "/" + date[3:5] + "/20" + date[6:8]
                        invoice_dash_date = "20" + date[6:8] + "-" + date[3:5] + "-" + date[:2]
                        promo_df = all_scrubbed_df.loc[all_scrubbed_df["Promotion_No"] == promotion_no]
                        for inv_date in [invoice_date, invoice_dash_date]:
                            promo_date_df = promo_df.loc[promo_df["Invoice_Date"] == inv_date]
                            invoice_list = promo_date_df["Invoice_No"].unique()
                            if len(invoice_list) == 1:
                                update_hdr_invoice(hdr_invoice, invoice_list[0])
                                processed_count += 1
                                updated = True
                                break
                if not updated and retailer_code == 'MOR01':
                    logger.debug(f"HDR Invoice '{hdr_invoice}' not found with MOR01 rules.")
    logger.info(f"Updated {processed_count} of {total_count} invoices.")



def main(client_arg, retailer_arg):
    """Main function to coordinate the invoice processing."""
    start_time = time.time()
    logger.info("Script execution started.")

    if client_arg == "manual":
        client_code = input("What's the Client Code? > ")
        retailer_code = input("What's the Retailer Code? > ")
    else:
        client_code = CLIENT_CODE_MAP.get(client_arg)
        retailer_code = RETAILER_CODE_MAP.get(retailer_arg)

        if not client_code:
            logger.error(f"Invalid client argument: {client_arg}.  Valid values are: {', '.join(CLIENT_CODE_MAP.keys())}, or 'manual'")
            sys.exit(1)
        if not retailer_code:
            logger.error(f"Invalid retailer argument: {retailer_arg}. Valid values are: {', '.join(RETAILER_CODE_MAP.keys())}, or 'manual'")
            sys.exit(1)

    logger.info(f"Processing data for client: {client_code}, retailer: {retailer_code}")
    client_db = get_client_db(client_code)
    if client_db is None:
        logger.error(f"Failed to retrieve client database name. Exiting.")
        sys.exit(1)

    hdr_list = get_hdr_invoices(client_db, retailer_code)
    cc_list = get_scrubbed_invoices(client_code, retailer_code)
    all_scrubbed_df = get_all_scrubbed_data(client_code, retailer_code)

    process_invoices(hdr_list, cc_list, all_scrubbed_df, retailer_code, client_code)
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"Script execution completed in {execution_time:.2f} seconds.")



if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.error("Usage: python script.py <client> <retailer>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
