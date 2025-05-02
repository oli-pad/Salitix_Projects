import logging
import pyodbc
import datetime


class DatabaseHandler(logging.Handler):
    def __init__(self, connection_string):
        super().__init__()
        self.connection_string = connection_string
        self.formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s - %(module)s - %(funcName)s')

    def emit(self, record):
        try:
            formatted_record = self.formatter.format(record)
            with pyodbc.connect(self.connection_string, autocommit=True) as conn:
                cursor = conn.cursor()
                dt_object = datetime.datetime.fromtimestamp(record.created)
                dt_string = dt_object.isoformat()  # Convert to ISO 8601 string
                max_message_length = 4000  # Set your desired maximum length
                truncated_message = record.message[:max_message_length]
                cursor.execute(
                    "INSERT INTO [Salitix_Master_Data].[dbo].[Salitix_Python_Log] ([timestamp], [level], [message], [module], [function]) VALUES (?, ?, ?, ?, ?)",
                    dt_string, record.levelname, truncated_message, record.module, record.funcName
                )
        except pyodbc.Error as e:
            print(f"Database logging error: {e}")


def setup_database_logger(connection_string, logger_name=__name__):
    """Sets up a logger that logs to the database."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    db_handler = DatabaseHandler(connection_string)
    logger.addHandler(db_handler)
    return logger
