import mysql.connector
import os
import sys

# Import functions from seed.py
# This assumes seed.py is in the same directory or accessible via PYTHONPATH
try:
    from seed import connect_to_prodev, TABLE_NAME
except ImportError:
    print("Error: Could not import 'connect_to_prodev' or 'TABLE_NAME' from seed.py.")
    print("Please ensure seed.py is in the same directory and is correctly configured.")
    sys.exit(1)

def stream_users():
    """
    Connects to the ALX_prodev database and streams rows from the 'user_data' table
    one by one using a generator.

    Yields:
        dict: A dictionary representing a single user row.
              Keys are column names, values are row data.
    """
    connection = None
    cursor = None
    try:
        # Establish connection to the ALX_prodev database
        # Use dictionary=True to fetch rows as dictionaries
        connection = connect_to_prodev()
        if connection is None:
            print("Failed to connect to the database. Cannot stream users.")
            return # Exit generator if connection fails

        # Create a cursor that returns rows as dictionaries
        cursor = connection.cursor(dictionary=True)

        # Execute the query to select all data from user_data table
        select_query = f"SELECT user_id, name, email, age FROM {TABLE_NAME}"
        cursor.execute(select_query)

        # Loop to fetch and yield rows one by one
        # This loop will continue as long as fetchone() returns a row
        # and will terminate when fetchone() returns None.
        while True:
            row = cursor.fetchone()
            if row is None:
                break # Exit the loop when no more rows are available
            yield row # Yield the current row

    except mysql.connector.Error as err:
        print(f"Error during database operation: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure cursor and connection are closed even if an error occurs
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            # print("Database connection closed.") # Optional: for debugging connection closure

