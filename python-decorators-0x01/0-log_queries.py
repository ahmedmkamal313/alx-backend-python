import sqllite3
import functools
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_queries(func):
    """
    A decorator that logs the SQL query string before the decorated function
    executes it.

    Assumes the decorated function takes the SQL query as its first positional
    argument or as a keyword argument named 'query'.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = None
        if args:
            # Check if the first argument is a string (the query)
            if isinstance(args[0], str) and ('SELECT' in args[0] or 'INSERT' in args[0] or 'UPDATE' in args[0] or 'DELETE' in args[0]):
                query = args[0]
        # If not found in args, check kwargs
        if query in kwargs:
            query = kwargs['query']
        
        if query:
            logging.info(f"Executing query: {query}")
        else:
            logging.warning("No query string found to log.")

        return func(*args, **kwargs)
    return wrapper

# Example usage (as provided in the task)
def fetch_all_users(query):
    """
    Fetches all users from the 'users.db' SQLite database.
    """
    conn = sqllite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Create a dummy database and table for testing the decorator
def setup_db():
    conn = sqllite3.connect('users.db')
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
    logging.info("Dummy 'users.db' created and populated.")

if __name__ == "__main__":
    setup_db() # Ensure the database is set up for testing

    # Fetch users while logging the query
    print("\n--- Testing fetch_all_users ---")
    users = fetch_all_users(query="SELECT * FROM users")
    print(f"Fetched users: {users}")

    print("\n--- Testing with a different query ---")
    specific_user = fetch_all_users(query="SELECT name, email FROM users WHERE id = 1")
    print(f"Fetched specific user: {specific_user}")

    print("\n--- Testing with positional argument (if function signature allows) ---")