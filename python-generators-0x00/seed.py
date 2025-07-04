import mysql.connector
import csv
import uuid
import os

# Database configuration (IMPORTANT: Password now read from environment variable)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    # Read password from environment variable
    'password': os.getenv('MYSQL_ROOT_PASSWORD'),
}

DATABASE_NAME = 'ALX_prodev'
TABLE_NAME = 'user_data'


def connect_db():
    """
    Connects to the MySQL database server.
    Returns a connection object if successful, None otherwise.
    """
    # Check if password is set
    if DB_CONFIG['password'] is None:
        print("Error: MySQL root password not found in environment variable 'MYSQL_ROOT_PASSWORD'.")
        print("Please set it using: export MYSQL_ROOT_PASSWORD='your_password'")
        return None

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to MySQL server.")
            return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL server: {err}")
        return None


def create_database(connection):
    """
    Creates the ALX_prodev database if it does not exist.
    Requires a connection to the MySQL server (not necessarily to a specific database).
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
        print(
            f"Database '{DATABASE_NAME}' created successfully or already exists.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating database '{DATABASE_NAME}': {err}")


def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL.
    Returns a connection object to ALX_prodev if successful, None otherwise.
    """
    # Check if password is set
    if DB_CONFIG['password'] is None:
        print("Error: MySQL root password not found in environment variable 'MYSQL_ROOT_PASSWORD'.")
        print("Please set it using: export MYSQL_ROOT_PASSWORD='your_password'")
        return None

    try:
        db_config_with_db = DB_CONFIG.copy()
        # Add database name to config
        db_config_with_db['database'] = DATABASE_NAME
        connection = mysql.connector.connect(**db_config_with_db)
        if connection.is_connected():
            print(f"Successfully connected to database '{DATABASE_NAME}'.")
            return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database '{DATABASE_NAME}': {err}")
        return None


def create_table(connection):
    """
    Creates the 'user_data' table if it does not exist with the required fields.
    Requires a connection to the ALX_prodev database.
    """
    try:
        cursor = connection.cursor()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            age DECIMAL(5,0) NOT NULL
        )
        """
        cursor.execute(create_table_query)
        connection.commit()  # Commit the table creation
        print(f"Table '{TABLE_NAME}' created successfully or already exists.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating table '{TABLE_NAME}': {err}")


def insert_data(connection, csv_file_path):
    """
    Inserts data from a CSV file into the 'user_data' table.
    It checks if a user_id already exists before inserting to prevent duplicates.
    Requires a connection to the ALX_prodev database.
    """
    try:
        cursor = connection.cursor()
        with open(csv_file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip header row

            # Determine column indices dynamically to be robust to CSV column order
            try:
                user_id_idx = header.index('user_id')
                name_idx = header.index('name')
                email_idx = header.index('email')
                age_idx = header.index('age')
            except ValueError as e:
                print(f"Error: Missing expected column in CSV header: {e}")
                return

            inserted_count = 0
            skipped_count = 0

            for row in reader:
                if len(row) < max(user_id_idx, name_idx, email_idx, age_idx) + 1:
                    print(f"Warning: Skipping malformed row: {row}")
                    continue

                user_id = row[user_id_idx]
                name = row[name_idx]
                email = row[email_idx]
                age = row[age_idx]

                # Check if user_id already exists to prevent duplicate inserts on re-run
                check_query = f"SELECT user_id FROM {TABLE_NAME} WHERE user_id = %s"
                cursor.execute(check_query, (user_id,))
                if cursor.fetchone():
                    # print(f"User with ID {user_id} already exists. Skipping insertion.")
                    skipped_count += 1
                    continue

                insert_query = f"""
                INSERT INTO {TABLE_NAME} (user_id, name, email, age)
                VALUES (%s, %s, %s, %s)
                """
                try:
                    cursor.execute(insert_query, (user_id, name, email, age))
                    connection.commit()  # Commit each row for simplicity, or commit in batches
                    inserted_count += 1
                except mysql.connector.Error as insert_err:
                    print(
                        f"Error inserting data for user_id {user_id} ({email}): {insert_err}")
                    connection.rollback()  # Rollback on individual row error
        print(f"Data insertion complete from '{csv_file_path}'.")
        print(f"Successfully inserted {inserted_count} new records.")
        print(f"Skipped {skipped_count} existing records.")
        cursor.close()
    except FileNotFoundError:
        print(
            f"Error: CSV file '{csv_file_path}' not found. Please ensure it's in the same directory.")
    except Exception as e:
        print(f"An unexpected error occurred during data insertion: {e}")
