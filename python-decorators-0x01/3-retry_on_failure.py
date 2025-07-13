import time
import sqlite3
import functools
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def with_db_connection(func):
    """
    A decorator that automatically handles opening and closing a SQLite database
    connection. It passes the connection object as the first argument to the
    decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            # Open the database connection
            conn = sqlite3.connect('users.db')
            logging.info(f"Database connection opened for '{func.__name__}'.")

            # Pass the connection object as the first argument to the decorated function
            result = func(conn, *args, **kwargs)
            return result
        except sqlite3.Error as e:
            logging.error(f"Database error in '{func.__name__}': {e}")
            raise # Re-raise the exception after logging
        except Exception as e:
            logging.error(f"An unexpected error occurred in '{func.__name__}': {e}")
            raise
        finally:
            # Ensure the connection is closed, even if an error occurred
            if conn:
                conn.close()
                logging.info(f"Database connection closed for '{func.__name__}'.")
    return wrapper

# --- Start of retry_on_failure decorator ---
def retry_on_failure(retries=3, delay=2):
    """
    A decorator that retries the decorated function a specified number of times
    if it raises an exception.

    Args:
        retries (int): The maximum number of times to retry the function.
        delay (int): The delay in seconds between retries.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries + 1): # +1 to include the initial attempt
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i < retries:
                        logging.warning(f"Attempt {i + 1}/{retries + 1} failed for '{func.__name__}': {e}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        logging.error(f"All {retries + 1} attempts failed for '{func.__name__}': {e}. No more retries.")
                        raise # Re-raise the last exception if all retries fail
        return wrapper
    return decorator
# --- End of retry_on_failure decorator ---

# Global counter to simulate transient failures for testing
_failure_count = 0
_max_failures = 2

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """
    Fetches all users from the 'users.db' database.
    Simulates a transient error for demonstration purposes.
    """
    global _failure_count
    if _failure_count < _max_failures:
        _failure_count += 1
        logging.warning(f"Simulating transient database error (call {_failure_count})...")
        raise sqlite3.OperationalError("Database is busy (simulated)")
    
    logging.info("Fetching users from the database.")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

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
    # Insert some dummy data if the table is empty
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice Smith', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob Johnson', 'bob@example.com')")
    conn.commit()
    conn.close()
    logging.info("Dummy 'users.db' created and populated for retry decorator test.")

if __name__ == "__main__":
    setup_db() # Ensure the database is set up for testing

    print("\n--- Attempting to fetch users with automatic retry ---")
    try:
        users = fetch_users_with_retry()
        print(f"Fetched users successfully: {users}")
    except Exception as e:
        print(f"Failed to fetch users after multiple retries: {e}")

    # Reset failure count for another test if needed
    _failure_count = 0
    print("\n--- Attempting to fetch users (should succeed on first try now, if _max_failures was lower) ---")
    try:
        users_again = fetch_users_with_retry()
        print(f"Fetched users successfully on second run: {users_again}")
    except Exception as e:
        print(f"Failed to fetch users on second run: {e}")