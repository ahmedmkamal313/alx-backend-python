import sqlite3
import functools
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def with_db_connection(func):
    """
    A decorator that provides a database connection to the decorated function.
    The function should accept a 'connection' keyword argument.
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
            raise  # Re-raise the exception after logging
        except Exception as e:
            logging.error(
                f"An unexpected error occurred in '{func.__name__}': {e}")
            raise
        finally:
            # Ensure the connection is closed, even if an error occurred
            if conn:
                conn.close()
                logging.info(
                    f"Database connection closed for '{func.__name__}'.")
    return wrapper

# --- Start of transactional decorator ---


def transactional(func):
    """
    A decorator that ensures a function running a database operation is wrapped
    inside a transaction. If the function raises an error, it rolls back the
    transaction; otherwise, it commits the transaction.

    Assumes the decorated function receives the database connection as its
    first argument.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):  # Expects 'conn' as the first argument
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()  # Commit changes if function executes successfully
            logging.info(f"Transaction committed for '{func.__name__}'.")
            return result
        except Exception as e:
            conn.rollback()  # Rollback changes if an error occurs
            logging.error(
                f"Transaction rolled back for '{func.__name__}' due to error: {e}")
            raise  # Re-raise the exception to propagate it
    return wrapper
# --- End of transactional decorator ---


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """
    Updates a user's email in the 'users' table.
    Demonstrates automatic transaction handling.
    """
    logging.info(
        f"Attempting to update email for user ID {user_id} to '{new_email}'.")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?",
                   (new_email, user_id))
    logging.info(f"Email update command executed for user ID {user_id}.")


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
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice Smith', 'alice@example.com')")
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob Johnson', 'bob@example.com')")
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email) VALUES (3, 'Charlie Brown', 'charlie@example.com')")
    conn.commit()
    conn.close()
    logging.info(
        "Dummy 'users.db' created and populated for transactional decorator test.")


def get_user_email(user_id):
    """Helper function to fetch user email for verification."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    email = cursor.fetchone()
    conn.close()
    return email[0] if email else None


if __name__ == "__main__":
    setup_db()  # Ensure the database is set up for testing

    print("\n--- Test Case 1: Successful Update ---")
    user_id_success = 1
    new_email_success = 'alice.updated@example.com'
    initial_email_success = get_user_email(user_id_success)
    print(f"Initial email for user {user_id_success}: {initial_email_success}")
    try:
        update_user_email(user_id=user_id_success, new_email=new_email_success)
        final_email_success = get_user_email(user_id_success)
        print(f"Final email for user {user_id_success}: {final_email_success}")
        assert final_email_success == new_email_success
        print("Update successful and committed.")
    except Exception as e:
        print(f"Error during update: {e}")
    print("-" * 30)

    print("\n--- Test Case 2: Simulated Rollback ---")
    user_id_rollback = 2
    new_email_rollback = 'bob.new@example.com'
    initial_email_rollback = get_user_email(user_id_rollback)
    print(
        f"Initial email for user {user_id_rollback}: {initial_email_rollback}")
    try:
        # Need a connection to pass to the decorated function
        conn_for_test = sqlite3.connect('users.db')

        @with_db_connection
        @transactional
        def update_user_email_with_simulated_error(conn, user_id, new_email):
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
            cursor.non_existent_method()

        update_user_email_with_simulated_error(
            user_id=user_id_rollback, new_email=new_email_rollback)
        final_email_rollback = get_user_email(user_id_rollback)
        print(
            f"Final email for user {user_id_rollback}: {final_email_rollback}")
        print(
            "Update attempted, but an error occurred. Check logs for rollback confirmation.")
    except Exception as e:
        print(f"Caught expected error: {e}")
        final_email_rollback = get_user_email(user_id_rollback)
        print(
            f"Email after rollback attempt for user {user_id_rollback}: {final_email_rollback}")
        assert final_email_rollback == initial_email_rollback
        print("Rollback successful: Email remained unchanged.")
    print("-" * 30)
