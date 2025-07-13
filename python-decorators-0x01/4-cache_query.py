import time
import sqlite3
import functools
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Global cache dictionary
query_cache = {}

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

# --- Start of cache_query decorator ---
def cache_query(func):
    """
    A decorator that caches query results based on the SQL query string.
    It stores results in the global `query_cache` dictionary.

    Assumes the decorated function receives the database connection as its
    first argument and the SQL query string as its second argument (or 'query' kwarg).
    """
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs): # Expects conn and query as first two args
        # Use the query string as the cache key
        cache_key = query

        if cache_key in query_cache:
            logging.info(f"Cache hit for query: '{query}'")
            return query_cache[cache_key]
        else:
            logging.info(f"Cache miss for query: '{query}'. Executing query...")
            # Execute the original function (which will run the query)
            result = func(conn, query, *args, **kwargs)
            query_cache[cache_key] = result # Store the result in cache
            logging.info(f"Query result cached for: '{query}'.")
            return result
    return wrapper
# --- End of cache_query decorator ---

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """
    Fetches users from the 'users.db' database.
    Results are cached by the @cache_query decorator.
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# --- Setup for demonstration ---
# Create a dummy database and table for testing the decorator
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
    logging.info("Dummy 'users.db' created and populated for cache decorator test.")

if __name__ == "__main__":
    setup_db()  # Ensure the database is set up for testing

    print("\n--- First call: Should execute query and cache result ---")
    start_time = time.time()
    users = fetch_users_with_cache(query="SELECT * FROM users")
    end_time = time.time()
    print(f"Fetched users (first call): {users}")
    print(f"Time taken (first call): {end_time - start_time:.4f} seconds")
    print(f"Cache content: {query_cache}")

    print("\n--- Second call: Should use cached result ---")
    start_time = time.time()
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    end_time = time.time()
    print(f"Fetched users (second call): {users_again}")
    print(f"Time taken (second call): {end_time - start_time:.4f} seconds (should be faster)")
    print(f"Cache content: {query_cache}")

    print("\n--- Third call with a different query: Should execute and cache new result ---")
    start_time = time.time()
    user_alice = fetch_users_with_cache(query="SELECT * FROM users WHERE id = 1")
    end_time = time.time()
    print(f"Fetched user Alice (third call): {user_alice}")
    print(f"Time taken (third call): {end_time - start_time:.4f} seconds")
    print(f"Cache content: {query_cache}")

    print("\n--- Fourth call with the different query again: Should use cached result ---")
    start_time = time.time()
    user_alice_again = fetch_users_with_cache(query="SELECT * FROM users WHERE id = 1")
    end_time = time.time()
    print(f"Fetched user Alice (fourth call): {user_alice_again}")
    print(f"Time taken (fourth call): {end_time - start_time:.4f} seconds (should be faster)")
    print(f"Cache content: {query_cache}")