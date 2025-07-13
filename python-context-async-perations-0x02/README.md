# 🔁 Python Context Managers and Asynchronous Operations

This project demonstrates how to implement custom **context managers** and perform **asynchronous database operations** in Python for safe and scalable backend development.

---

## 🎯 Purpose

This project illustrates how to:

- ✅ Implement a **class-based context manager** using `__enter__` and `__exit__` methods to automatically handle resource management (e.g., database connections).
- ✅ Use the `with` statement for **cleaner, safer** code.
- ✅ Build a reusable context manager for **executing queries**, abstracting away connection boilerplate.
- ✅ Perform **asynchronous database operations** using `asyncio` and `aiosqlite` to improve performance for I/O-bound tasks.

---

## 📂 Files in this Directory

| File | Description |
|------|-------------|
| `0-databaseconnection.py` | Contains `DatabaseConnection`, a custom context manager for SQLite connections and query execution. |
| `1-execute.py` | Contains `ExecuteQuery`, a reusable query execution context manager. |
| `3-concurrent.py` | Demonstrates **async/await** usage with `aiosqlite` for concurrent DB queries using `asyncio.gather()`. |

---

## ⚙️ Setup and Usage

1. **Navigate to the directory**

```bash
cd python-context-async-operations-0x02
```

2. **Install dependencies**

```bash
pip install aiosqlite
```

3. **Run the examples**

    Run context manager for database connection:

    ```bash
    python3 0-databaseconnection.py
    ```
    Run reusable query context manager:

    ```bash
    python3 1-execute.py
    ```
    Run async concurrent database operations:

    ```bash
    python3 3-concurrent.py
    ```
--- 

## ✅ Expected Output
You'll see printed logs such as:

    - Opening/closing of database connections

    - Execution of SQL queries

    - Inserted or retrieved data

    - Concurrent async results side-by-side using asyncio.gather()

This provides both safety (via context management) and scalability (via async).

---

## 🧠 Key Concepts Demonstrated
- Context management with __enter__/__exit__
- DRY principles using reusable decorators/classes
- Safe SQLite operations
- Asynchronous programming (async, await, gather)
- Efficient I/O handling for backend operations