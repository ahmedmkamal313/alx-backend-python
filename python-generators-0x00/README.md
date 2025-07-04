# 🐍 Python Generators Project – Database Seeding & Streaming

This project demonstrates how to **seed and stream data from a MySQL database** using **Python generator functions**. It focuses on **memory-efficient** data handling and lazy evaluation, suitable for large-scale datasets.

---

## 🎯 Project Purpose

This directory showcases:

- 📦 **Database Setup & Seeding**: Load user data into MySQL from a CSV file  
- 🔁 **Row-by-Row Streaming**: Use a generator to iterate over results without loading all into memory  
- 📚 **Batch Processing**: Process database rows in configurable chunks  
- 📄 **Lazy Pagination**: Fetch and display paginated results only when needed  
- 📊 **On-the-Fly Aggregation**: Calculate statistics (e.g., average age) with minimal memory usage  

---

## 🛠️ Database Schema

This project assumes a `user_data` table with the following structure:

| Column    | Type          | Description                           |
|-----------|---------------|---------------------------------------|
| `user_id` | `CHAR(36)`    | Primary key, stores UUIDs             |
| `name`    | `VARCHAR(255)`| User’s full name, not null            |
| `email`   | `VARCHAR(255)`| Must be unique, not null              |
| `age`     | `DECIMAL(5,0)`| Age of the user, not null             |

> Database: **ALX_prodev**

---

## 📁 Files Overview

### 📌 `seed.py`
- Connects to MySQL  
- Creates the `ALX_prodev` database and `user_data` table  
- Seeds user data from a CSV file  

---

### 🔄 `0-stream_users.py`
- Implements `stream_users()` generator  
- Streams rows **one at a time** using a cursor (low memory usage)  

---

### 📦 `1-batch_processing.py`
- Implements:
  - `stream_users_in_batches(batch_size)` → generator that yields user records in chunks  
  - `batch_processing(batch_size)` → filters and processes data in batches (e.g., by age or name)  

---

### 📄 `2-lazy_paginate.py`
- Implements:
  - `paginate_users(page_size)` → fetches fixed-size pages from the DB  
  - `lazy_pagination()` → generator that lazily fetches only when the next page is needed  

---

### 📊 `4-stream_ages.py`
- Implements:
  - `stream_user_ages()` → generator to yield only age values  
  - `average_age()` → computes the average **without loading all ages into memory**  

---

## ✅ Key Concepts Demonstrated

- ✅ **Generators** for memory-safe iteration  
- ✅ **Streaming large datasets** from a database  
- ✅ **Batch filtering and transformation**  
- ✅ **Lazy evaluation for pagination**  
- ✅ **Efficient aggregation without full table scans**  

---

## 👤 Author

**Ahmed Kamal**  
[🔗 GitHub: ahmedmkamal313](https://github.com/ahmedmkamal313)
