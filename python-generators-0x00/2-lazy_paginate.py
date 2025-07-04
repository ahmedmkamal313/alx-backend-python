import mysql.connector
import os
import sys

# Import connect_to_prodev from seed.py
try:
    from seed import connect_to_prodev
except ImportError:
    print("Error: Could not import 'connect_to_prodev' from seed.py.")
    print("Please ensure seed.py is in the same directory and is correctly configured.")
    sys.exit(1)


def paginate_users(page_size, offset):
    """
    Fetches a specific page of user data from the 'user_data' table.

    Args:
        page_size (int): The maximum number of rows to fetch for the current page.
        offset (int): The starting point (offset) for fetching rows.

    Returns:
        list of dict: A list of dictionaries, where each dictionary represents a user row.
                      Returns an empty list if no more rows are available.
    """
    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        if connection is None:
            print("Failed to connect to the database. Cannot paginate users.")
            return []

        cursor = connection.cursor(dictionary=True)
        # Use parameterized query to prevent SQL injection, though LIMIT/OFFSET are integers here
        select_query = f"SELECT user_id, name, email, age FROM user_data LIMIT %s OFFSET %s"
        cursor.execute(select_query, (page_size, offset))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error during database operation in paginate_users: {err}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred in paginate_users: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def lazy_pagination(page_size):
    """
    Implements a generator function to lazily load paginated data from the
    'user_data' table. It fetches the next page only when needed.

    Args:
        page_size (int): The number of rows to fetch per page.

    Yields:
        list of dict: A list of dictionaries, representing a page of user data.
                      Each yield returns a full page.
    """
    if not isinstance(page_size, int) or page_size <= 0:
        raise ValueError("page_size must be a positive integer.")

    offset = 0
    # Loop 1: Continuously fetches pages until no more data is found
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break  # Exit the loop if the fetched page is empty (no more data)
        yield page  # Yield the current page
        offset += page_size  # Increment offset for the next page
