# 🧠 ALX Backend Python

Welcome to the **ALX Backend Python** repository — a collection of backend-focused Python projects showcasing advanced data processing, performance optimization, and scalable architecture concepts using clean, efficient, and idiomatic Python.

---

## 🚀 Project Purpose

This repo serves as a **consolidated workspace** for exploring backend programming with Python through real-world inspired challenges.

---

## 📁 Directory Structure

```bash
alx-backend-python/
│
├── python-generators-0x00/           # MySQL data streaming & batching with generators
├── python-decorators-0x01/           # SQL decorators: logging, retries, caching, and connection handling
├── python-context-async-perations-0x02/
|
└── README.md                         # You're here
```
---
> ✅ Modular and scalable — each directory represents a fully self-contained backend project.

---

## 🐍 Highlight: Generators Project

📁 [`python-generators-0x00`](./python-generators-0x00)

A project focused on using **Python generators** for efficient streaming of data from a MySQL database, especially helpful when working with large datasets that cannot fit in memory.

### 🔍 Features
- ✅ **Row-by-row streaming** from the database
- ✅ **Batch-wise filtering** for scalable processing
- ✅ **Lazy pagination** for UI/CLI-based consumption
- ✅ **Aggregation** with minimal memory footprint
- ✅ Includes **database seeding** from CSV

> 📘 Full Details: [`python-generators-0x00/README.md`](./python-generators-0x00/README.md)

---

## ⚙️ Highlight: Decorators Project

📁 [`python-decorators-0x01`](./python-decorators-0x01)

This project demonstrates how to enhance Python database code using **custom decorators** that wrap functionality like logging, connection management, retries, transactions, and caching.

### 🔍 Features
- ✅ `@log_queries`: Log SQL queries before execution
- ✅ `@with_db_connection`: Automatically manage DB connections
- ✅ `@transactional`: Auto-commit or rollback logic
- ✅ `@retry_on_failure`: Retry failed operations gracefully
- ✅ `@cache_query`: Memory-efficient query result caching

> 📘 Full Details: [`python-decorators-0x01/README.md`](./python-decorators-0x01/README.md)

---

#### 🔁 Highlight: Context Managers & Async Operations

📁 [`python-context-async-operations-0x02`](./python-context-async-operations-0x02)

This project focuses on building **custom context managers** for resource-safe SQLite operations and using **asynchronous Python** for concurrent database querying.

### 🔍 Features
- ✅ `with`-based automatic connection management
- ✅ Reusable SQL execution context manager
- ✅ Safe commit/rollback behavior
- ✅ Async fetching of large datasets using `aiosqlite`
- ✅ Parallel DB queries with `asyncio.gather()`

> 📘 Full Details: [`python-context-async-operations-0x02/README.md`](./python-context-async-operations-0x02/README.md)

---
## 📚 Prerequisites

- Python 3.8+  
- MySQL Server (for Generators Project)  
- SQLite (for Decorators Project)  
- Required Python packages (see each project's README)

