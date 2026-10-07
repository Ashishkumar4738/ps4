
from logger_config import logger
import sqlite3

from config.config import DATABASE_FILE, DATA_DIR



def get_connection():
    """
    Create and return a SQLite database connection.
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        str(DATABASE_FILE),
        timeout=10,
    )

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection
