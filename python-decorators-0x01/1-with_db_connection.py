import sqlite3
import functools
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def with_db_connection(func):
    """
    A decorator that provides a database connection to the decorated function.
    The function should accept a 'connection' keyword argument.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            # Open a database connection
            conn = sqlite3.connect('users.db')
            logging.info("Database connection established.")

            # Pass the connection object as the first argument to the decorated function
            result = func(conn, *args, **kwargs)
            return result
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise
        finally:
            # Ensure the connection is closed
            if conn:
                conn.close()
                logging.info("Database connection closed.")
    return wrapper

@with_db_connection
def setup_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice Smith', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob Johnson', 'bob@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (3, 'Charlie Brown', 'charlie@example.com')")
    conn.commit()
    conn.close()
    logging.info("Dummy 'users.db' created and populated for connection decorator test.")

if __name__ == "__main__":
    setup_db() # Ensure the database is set up for testing

    print("\n--- Testing get_user_by_id with automatic connection handling ---")
    # Fetch user by ID with automatic connection handling
    user_id_to_fetch = 1
    user = get_user_by_id(user_id=user_id_to_fetch) # conn is passed automatically by decorator
    print(f"Fetched user with ID {user_id_to_fetch}: {user}")

    user_id_to_fetch = 2
    user = get_user_by_id(user_id=user_id_to_fetch)
    print(f"Fetched user with ID {user_id_to_fetch}: {user}")

    print("\n--- Testing a non-existent user ---")
    user_id_to_fetch = 99
    user = get_user_by_id(user_id=user_id_to_fetch)
    print(f"Fetched user with ID {user_id_to_fetch}: {user}")