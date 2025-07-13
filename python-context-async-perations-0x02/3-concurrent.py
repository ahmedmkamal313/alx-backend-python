import asyncio
import aiosqlite  # For asynchronous SQLite interaction
import logging
import os  # For removing the database file for clean setup

# Configure basic logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

DB_NAME = 'users.db'


def setup_db(db_name=DB_NAME):
    """
    Sets up a dummy SQLite database and populates it with sample data.
    This function is synchronous as it's for initial setup.
    Ensures there are users older than 40 for testing.
    """
    # Remove existing db for a clean test each time
    if os.path.exists(db_name):
        os.remove(db_name)
        logging.info(f"Removed existing database: {db_name}")

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
    # Insert some dummy data, ensuring some users are older than 40
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email, age) VALUES (1, 'Alice Smith', 'alice@example.com', 30)")
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email, age) VALUES (2, 'Bob Johnson', 'bob@example.com', 22)")
    # Older than 40
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email, age) VALUES (3, 'Charlie Brown', 'charlie@example.com', 45)")
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email, age) VALUES (4, 'Diana Miller', 'diana@example.com', 28)")
    # Older than 40
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email, age) VALUES (5, 'Eve Davis', 'eve@example.com', 55)")
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email, age) VALUES (6, 'Frank White', 'frank@example.com', 38)")
    conn.commit()
    conn.close()
    logging.info(
        f"Dummy '{db_name}' created and populated for concurrent query test.")


async def async_fetch_users():
    """
    Asynchronously fetches all users from the database.
    """
    logging.info("Starting async_fetch_users...")
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            users = await cursor.fetchall()
            logging.info(
                f"Finished async_fetch_users. Fetched {len(users)} users.")
            return users


async def async_fetch_older_users():
    """
    Asynchronously fetches users older than 40 from the database.
    """
    logging.info("Starting async_fetch_older_users...")
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            older_users = await cursor.fetchall()
            logging.info(
                f"Finished async_fetch_older_users. Fetched {len(older_users)} older users.")
            return older_users


async def fetch_concurrently():
    """
    Executes async_fetch_users and async_fetch_older_users concurrently
    using asyncio.gather.
    """
    logging.info("Starting concurrent fetch operations...")
    # asyncio.gather runs awaitables concurrently and returns their results in order
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    logging.info("Concurrent fetch operations completed.")
    return all_users, older_users

if __name__ == "__main__":
    setup_db()  # Ensure the database is set up before running async operations

    print("\n--- Running concurrent database queries ---")
    try:
        # Run the main asynchronous function
        all_users_data, older_users_data = asyncio.run(fetch_concurrently())

        print("\nResults from async_fetch_users:")
        for user in all_users_data:
            print(user)

        print("\nResults from async_fetch_older_users:")
        for user in older_users_data:
            print(user)

    except Exception as e:
        logging.error(f"An error occurred during concurrent execution: {e}")
