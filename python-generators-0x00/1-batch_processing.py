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


def stream_users_in_batches(batch_size):
    """
    Connects to the ALX_prodev database and streams rows from the 'user_data' table
    in batches using a generator.

    Args:
        batch_size (int): The number of rows to fetch in each batch.

    Yields:
        list of dict: A list of dictionaries, where each dictionary represents a user row.
                      Each yield returns a batch of users.
    """
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer.")

    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        if connection is None:
            print("Failed to connect to the database. Cannot stream users in batches.")
            return  # Exit generator if connection fails

        cursor = connection.cursor(dictionary=True)
        select_query = f"SELECT user_id, name, email, age FROM {TABLE_NAME}"
        cursor.execute(select_query)

        # Loop 1: Fetches batches of rows
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break  # Exit loop if no more rows are fetched
            yield batch  # Yield the current batch of users

    except mysql.connector.Error as err:
        print(
            f"Error during database operation in stream_users_in_batches: {err}")
    except Exception as e:
        print(f"An unexpected error occurred in stream_users_in_batches: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def batch_processing(batch_size):
    """
    Processes users fetched in batches from the 'user_data' table,
    filtering for users over the age of 25.

    Args:
        batch_size (int): The number of rows to fetch in each batch for processing.

    Yields:
        dict: A dictionary representing a single user row that meets the age criteria.
    """
    # Loop 2: Iterates over batches yielded by stream_users_in_batches
    for batch in stream_users_in_batches(batch_size):
        # Loop 3: Iterates over individual users within the current batch
        for user in batch:
            # Ensure 'age' is treated as a number for comparison
            # It's DECIMAL(5,0) in DB, so it should come as a number type (int/float)
            try:
                # Convert age to int for comparison. Handle potential non-numeric age values.
                age = int(user.get('age'))
                if age > 25:
                    yield user  # Yield filtered user
            except (ValueError, TypeError):
                # Print a warning if age cannot be converted, but continue processing
                print(
                    f"Warning: Could not process age for user {user.get('user_id')}. Skipping.", file=sys.stderr)
                continue
