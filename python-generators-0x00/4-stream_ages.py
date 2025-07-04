import mysql.connector
import os
import sys

# Import connect_to_prodev from seed.py
try:
    from seed import connect_to_prodev, TABLE_NAME
except ImportError:
    print("Error: Could not import 'connect_to_prodev' or 'TABLE_NAME' from seed.py.")
    print("Please ensure seed.py is in the same directory and is correctly configured.")
    sys.exit(1)


def stream_user_ages():
    """
    Connects to the ALX_prodev database and yields user ages one by one
    from the 'user_data' table.

    Yields:
        int or float: The age of a single user.
    """
    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        if connection is None:
            print("Failed to connect to the database. Cannot stream user ages.")
            return  # Exit generator if connection fails

        # dictionary=True to get column names
        cursor = connection.cursor(dictionary=True)
        select_query = f"SELECT age FROM {TABLE_NAME}"
        cursor.execute(select_query)

        # Loop 1: Fetches and yields each age row by row
        while True:
            row = cursor.fetchone()
            if row is None:
                break  # Exit the loop when no more rows are available
            # Ensure age is returned as a numeric type for calculation
            # Convert to int as DECIMAL(5,0) implies whole numbers
            yield int(row['age'])

    except mysql.connector.Error as err:
        print(f"Error during database operation in stream_user_ages: {err}")
    except Exception as e:
        print(f"An unexpected error occurred in stream_user_ages: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def calculate_average_age_from_stream():
    """
    Calculates the average age of users by consuming ages from the stream_user_ages()
    generator, without loading the entire dataset into memory.

    Prints the average age to the console.
    """
    total_age = 0
    user_count = 0

    # Loop 2: Iterates over ages yielded by the generator
    for age in stream_user_ages():
        total_age += age
        user_count += 1

    if user_count > 0:
        average_age = total_age / user_count
        # Format to 2 decimal places
        print(f"Average age of users: {average_age:.2f}")
    else:
        print("No user data found to calculate average age.")


if __name__ == "__main__":
    calculate_average_age_from_stream()
