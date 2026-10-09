
from database.connection import get_connection
from tabulate import tabulate

connection = get_connection()

# tables

# documents
# meetings
# meeting_segments
# conversation_events

tables = [
    "documents",
    "meetings",
    "meeting_segments",
    "conversation_events"
]

for table in tables:
    print(f"\n{'=' * 60}")
    print(f"Table: {table}")
    print("=" * 60)

    cursor = connection.execute(f"PRAGMA table_info({table})")
    rows = cursor.fetchall()
    # Get column names automatically
    columns = [description[0] for description in cursor.description]

    # Print results in table format
    print(tabulate(rows, headers=columns, tablefmt="grid"))

# cursor = connection.execute("""
    
#     PRAGMA table_info(table);
# """)
# cursor = connection.execute("""
#     SELECT name
#     FROM sqlite_master
#     WHERE type = 'table'
#     ORDER BY name;
# """)

# rows = cursor.fetchall()

# # Get column names automatically
# columns = [description[0] for description in cursor.description]

# # Print results in table format
# print(tabulate(rows, headers=columns, tablefmt="grid"))
