# 🐍 Python Decorators Project – Query Logging, Connection Handling, Retries & Caching

This directory contains Python scripts that demonstrate the implementation of **custom decorators** to enhance database interaction logic with features like **SQL query logging**, **connection management**, **transaction handling**, **automatic retries**, and **result caching**.

---

## 🎯 Purpose

This project illustrates how to use decorators to:

- 🔍 **Log SQL queries** before execution with `@log_queries`, enhancing traceability and debugging.
- 🔌 **Automatically manage database connections** using `@with_db_connection` for cleaner code and safe resource handling.
- 🔒 **Wrap operations in transactions** using `@transactional` to ensure atomic commits or rollbacks on failure.
- 🔁 **Retry failed operations** due to transient errors using `@retry_on_failure`, improving reliability.
- ⚡ **Cache query results** with `@cache_query`, optimizing performance for frequently repeated queries.

---

## 📄 Files in This Directory

| File                      | Description                                                                                 |
|---------------------------|---------------------------------------------------------------------------------------------|
| `0-log_queries.py`        | Implements `@log_queries` and shows usage with a `fetch_all_users` function.               |
| `1-with_db_connection.py` | Implements `@with_db_connection` and demonstrates automatic DB connection management.       |
| `2-transactional.py`      | Adds `@transactional` decorator for handling transactions with rollback on failure.         |
| `3-retry_on_failure.py`   | Implements `@retry_on_failure` for retrying DB operations that fail due to transient issues.|
| `4-cache_query.py`        | Implements `@cache_query` to cache results and reduce redundant DB hits.                   |

Each script uses an SQLite database (`users.db`) and demonstrates its behavior through realistic examples.

---

## 🧪 Setup & Usage

### 🔹 Step 1: Navigate to the directory
```bash
cd python-decorators-0x01
```

### 🔹 Step 2: Run individual scripts

#### 🧾 Log SQL Queries
```bash
python3 0-log_queries.py
```
- Creates `users.db` if not exists, populates it, and logs SQL queries before execution.

#### 🔌 Database Connection Management
```bash
python3 1-with_db_connection.py
```
- Uses `@with_db_connection` to manage connections automatically when calling `get_user_by_id()`.

#### 🔄 Transaction Handling
```bash
python3 2-transactional.py
```
- Demonstrates `@transactional` to wrap updates like `update_user_email()` in safe transactions with commit/rollback.

#### 🔁 Retry on Failure
```bash
python3 3-retry_on_failure.py
```
- Automatically retries `fetch_users_with_retry()` if a transient database error is simulated.

#### ⚡ Query Caching
```bash
python3 4-cache_query.py
```
- Caches query results using `@cache_query` and shows cache hits/misses on repeated calls.

---

## 🧾 Expected Output

You’ll observe console logs showing:

- ✅ SQL queries being logged before execution
- 🔄 Database connections being opened/closed
- 🔁 Retry attempts with delays
- 💾 Transactions being committed or rolled back
- ⚙️ Cache hits and misses

Followed by the **actual database query results** printed to the console.

---

## 📚 Concepts Practiced

- Python decorators
- SQLite database interaction
- Functional abstraction
- Retry logic and exception handling
- In-memory caching for performance

---
