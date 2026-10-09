
from database.connection import get_connection
from tabulate import tabulate

connection = get_connection()

cursor = connection.execute("""
    SELECT * FROM documents
""")
# cursor = connection.execute("""
#     SELECT name
#     FROM sqlite_master
#     WHERE type = 'table'
#     ORDER BY name;
# """)

rows = cursor.fetchall()

# Get column names automatically
columns = [description[0] for description in cursor.description]

# Print results in table format
print(tabulate(rows, headers=columns, tablefmt="grid"))
