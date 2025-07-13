import sqlite3
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class DatabaseConnection:
    """
    A class-based context manager to handle opening and closing SQLite database connections automatically.
    """

    def __init__(self, db_name='users.db'):
        """
        Initializes the DatabaseConnection context manager.

        Args:
            db_name (str): The name of the SQLite database file.
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """
        Enters the runtime context related to this object.
        Opens the database connection and creates a cursor.

        Returns:
            sqlite3.Connection: The database connection object.
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            logging.info(f"Database connection to '{self.db_name}' opened.")
            return self.conn
        except sqlite3.Error as e:
            logging.error(f"Error opening database connection: {e}")
            raise  # Re-raise the exception to indicate failure to enter context

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the runtime context related to this object.
        Closes the database connection, handling exceptions.

        Args:
            exc_type (type): The type of the exception that caused the context to be exited.
            exc_val (Exception): The exception instance that caused the context to be exited.
            exc_tb (traceback): A traceback object encapsulating the call stack at the point where the exception originally occurred.
        """
        if exc_type:
            # An exception occurred within the 'with' block
            logging.error(
                f"An exception occurred in the 'with' block: {exc_val}")
            if self.conn:
                self.conn.rollback()  # Rollback changes on error
                logging.info("Transaction rolled back.")
        else:
            # No exception occurred, commit changes
            if self.conn:
                self.conn.commit()
                logging.info("Transaction committed.")

        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logging.info(f"Database connection to '{self.db_name}' closed.")

        # If an exception occurred, __exit__ should return False to propagate it,
        # or True to suppress it. We want to propagate it, so implicitly return None (False).

# --- Setup for demonstration ---
# Create a dummy database and table for testing the context manager


def setup_db(db_name='users.db'):
    conn = sqlite3.connect(db_name)
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
    conn.commit()
    conn.close()
    logging.info(
        f"Dummy '{db_name}' created and populated for context manager test.")


if __name__ == "__main__":
    db_file_name = 'users.db'
    setup_db(db_file_name)  # Ensure the database is set up

    print("\n--- Using DatabaseConnection context manager ---")
    try:
        # Use the context manager with the 'with' statement
        with DatabaseConnection(db_file_name) as conn:
            logging.info("Inside the 'with' block. Executing query...")
            cursor = conn.cursor()
            query = "SELECT * FROM users"
            cursor.execute(query)
            results = cursor.fetchall()
            print(f"Query results: {results}")

            # Simulate an update (will be committed on exit)
            cursor.execute(
                "UPDATE users SET name = ? WHERE id = ?", ("Alicia Smith", 1))
            logging.info("Update command executed for user 1.")

        print("\n--- Verifying update after context manager exits ---")
        with DatabaseConnection(db_file_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = 1")
            updated_user = cursor.fetchone()
            print(f"User 1 after update: {updated_user}")

        print("\n--- Testing rollback with an error ---")
        try:
            with DatabaseConnection(db_file_name) as conn:
                logging.info("Inside 'with' block for rollback test.")
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET name = ? WHERE id = ?", ("Failed Update", 2))
                logging.info(
                    "Update command executed for user 2 (should rollback).")
                raise ValueError("Simulating an error to trigger rollback")
        except ValueError as e:
            print(f"Caught expected error: {e}")

        print("\n--- Verifying rollback ---")
        with DatabaseConnection(db_file_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = 2")
            user_after_rollback = cursor.fetchone()
            print(f"User 2 after rollback attempt: {user_after_rollback}")
            # The name should still be 'Bob Johnson' if rollback worked
            assert user_after_rollback[1] == 'Bob Johnson'
            print("Rollback successful: User 2's name remained unchanged.")

    except Exception as e:
        print(f"An error occurred during main execution: {e}")
