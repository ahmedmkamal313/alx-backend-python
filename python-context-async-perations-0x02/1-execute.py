import sqlite3
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class ExecuteQuery:
    """
    A reusable class-based context manager that takes a query and parameters,
    executes it, and returns the results, managing the database connection.
    """

    def __init__(self, db_name='users.db', query=None, params=None):
        """
        Initializes the ExecuteQuery context manager.

        Args:
            db_name (str): The name of the SQLite database file.
            query (str): The SQL query string to execute.
            params (tuple, optional): Parameters for the SQL query. Defaults to None.
        """
        self.db_name = db_name
        self.query = query
        self.params = params if params is not None else ()
        self.conn = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        """
        Enters the runtime context. Opens the database connection,
        executes the query, and fetches the results.

        Returns:
            list: The results fetched from the database query.
        """
        if not self.query:
            raise ValueError("A SQL query must be provided to ExecuteQuery.")

        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            logging.info(
                f"Database connection to '{self.db_name}' opened for query: '{self.query}'.")

            self.cursor.execute(self.query, self.params)
            self.results = self.cursor.fetchall()
            logging.info(
                f"Query executed successfully. Fetched {len(self.results)} rows.")
            return self.results
        except sqlite3.Error as e:
            logging.error(f"Error executing query '{self.query}': {e}")
            if self.conn:
                self.conn.rollback()  # Rollback on error
                logging.info("Transaction rolled back due to error.")
            raise  # Re-raise the exception to propagate it
        except Exception as e:
            logging.error(
                f"An unexpected error occurred during query execution: {e}")
            if self.conn:
                self.conn.rollback()  # Rollback on error
                logging.info(
                    "Transaction rolled back due to unexpected error.")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the runtime context. Closes the database connection,
        committing changes if no exception occurred, or rolling back otherwise.
        """
        if exc_type:
            # An exception occurred within the 'with' block
            logging.error(
                f"An exception occurred in the 'with' block: {exc_val}")
            # Rollback is handled in __enter__ for query execution errors
            # but this catch is for errors *after* query execution but before exit.
            if self.conn:
                self.conn.rollback()
                logging.info(
                    "Transaction rolled back on exit due to exception.")
        else:
            # No exception occurred, commit changes (relevant for INSERT/UPDATE/DELETE)
            if self.conn:
                self.conn.commit()
                logging.info("Transaction committed on exit.")

        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logging.info(f"Database connection to '{self.db_name}' closed.")

        # Return False to propagate the exception if one occurred.

# --- Setup for demonstration ---
# Create a dummy database and table for testing


def setup_db(db_name='users.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER NOT NULL
        )
    ''')
    # Insert some dummy data if the table is empty
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email, age) VALUES (1, 'Alice Smith', 'alice@example.com', 30)")
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email, age) VALUES (2, 'Bob Johnson', 'bob@example.com', 22)")
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email, age) VALUES (3, 'Charlie Brown', 'charlie@example.com', 45)")
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email, age) VALUES (4, 'Diana Miller', 'diana@example.com', 28)")
    conn.commit()
    conn.close()
    logging.info(
        f"Dummy '{db_name}' created and populated for ExecuteQuery test.")


if __name__ == "__main__":
    db_file_name = 'users.db'
    setup_db(db_file_name)  # Ensure the database is set up

    print("\n--- Using ExecuteQuery for 'SELECT * FROM users WHERE age > ?' ---")
    try:
        query_str = "SELECT * FROM users WHERE age > ?"
        param_value = 25
        with ExecuteQuery(query=query_str, params=(param_value,)) as users_over_25:
            print(f"Users older than {param_value}: {users_over_25}")
    except Exception as e:
        print(f"An error occurred: {e}")

    print("\n--- Using ExecuteQuery for a simple 'SELECT *' ---")
    try:
        with ExecuteQuery(query="SELECT * FROM users") as all_users:
            print(f"All users: {all_users}")
    except Exception as e:
        print(f"An error occurred: {e}")

    print("\n--- Testing ExecuteQuery with an INSERT operation ---")
    try:
        new_user_id = 5
        new_user_name = "Eva Green"
        new_user_email = "eva@example.com"
        new_user_age = 35
        insert_query = "INSERT INTO users (id, name, email, age) VALUES (?, ?, ?, ?)"
        insert_params = (new_user_id, new_user_name,
                         new_user_email, new_user_age)
        with ExecuteQuery(query=insert_query, params=insert_params) as _:  # No results for INSERT
            print(f"User '{new_user_name}' inserted successfully.")

        # Verify insertion
        with ExecuteQuery(query="SELECT * FROM users WHERE id = ?", params=(new_user_id,)) as fetched_new_user:
            print(f"Newly inserted user: {fetched_new_user}")

    except Exception as e:
        print(f"An error occurred during INSERT test: {e}")

    print("\n--- Testing ExecuteQuery with a simulated error during query ---")
    try:
        # This query will cause a syntax error
        with ExecuteQuery(query="SELECT FROM users WHERE id = 1") as invalid_query_results:
            print(
                f"Invalid query results (should not print): {invalid_query_results}")
    except sqlite3.Error as e:
        print(f"Caught expected SQLite error for invalid query: {e}")
    except Exception as e:
        print(f"Caught unexpected error for invalid query: {e}")
