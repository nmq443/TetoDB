# TetoDB

**TetoDB** is a lightweight, disk-based relational database management system built from scratch in C++. It implements core database engine concepts including a custom B+ Tree indexing engine, a paged memory buffer pool (Pager), and a SQL-like command interface.

Designed for portability and performance, TetoDB relies on fixed-width binary serialization to ensure database files are consistent across Windows and Linux environments.

> **⚠️ IMPORTANT: DATA PERSISTENCE**
> TetoDB uses a **manual commit** system. Changes are held in the memory buffer pool and are NOT written to disk automatically.
> * You **MUST** run the `.commit` command to save your changes.
> * Exiting the program (`.exit` or Ctrl+C) **WITHOUT** committing will result in the loss of all unsaved data.
> 
> 

## 🚀 Features

* **Persistent Storage:** Data is stored in binary files using fixed 4KB pages, mimicking real-world database page sizes.
* **B+ Tree Indexing:** Supports fast lookups, range scans, and range deletions on integer columns.
* **Buffer Pool (Pager):** Manages file I/O with an in-memory cache, supporting lazy writes and manual commits.
* **Cross-Platform:** Compiles and runs natively on both **Windows** (using `_commit`, `<io.h>`) and **Linux** (using `fsync`, `<unistd.h>`).
* **Performance Profiling:** Built-in execution timer measures the processing time of every command in nanoseconds/milliseconds.
* **10 Million Row Scale:** Capable of handling massive datasets with sub-millisecond query times using B-Tree indexing.



## 📦 Installation & Build

No external dependencies are required. You only need a C++ compiler (g++, clang, or MSVC).

### ⚡ Critical: Compile for Performance

For accurate benchmarking, you **must** compile with the `-O3` optimization flag. Without it, the heavy math involved in B-Tree rebalancing will be significantly slower.

```bash
# Windows / Linux
g++ -O3 *.cpp -o TetoDB

```

*Note:* If using PowerShell on Windows, run as `./TetoDB.exe`.

## 📖 Usage

### Starting the Database

To open (or create) a database environment, run the executable with a name for your database files:

```bash
# Interactive Mode
./TetoDB my_db

```

### Running a Script

You can also pass a text file containing commands as a second argument:

```bash
# Execute commands from script.txt and then exit
./TetoDB my_db script.txt

```

### Supported Commands

#### 1. Create Table

Create a new table. For integer columns, the third argument specifies if it is indexed (`1` = Index, `0` = No Index). For char columns, it specifies the length.

```sql
-- Create table 'users' with an index on 'id' and a 32-byte string for 'name'
CREATE TABLE users id int 1 name char 32 age int 0

```

#### 2. Insert Data

Insert a row into the table. String values **must** be quoted.

```sql
INSERT INTO users 42 "Blue Teto" 16
INSERT INTO users 10 "Teto" 31

```

#### 3. Select Data

Perform a full table scan or a range query.

```sql
-- Select all rows
SELECT FROM users

-- Range Scan: Select rows where 'id' is between 10 and 50 (inclusive)
-- Syntax: SELECT FROM <table> WHERE <col> <min> <max>
SELECT FROM users WHERE id 10 50

```

#### 4. Delete Data

Delete all rows or specific rows using a range.

```sql
-- Delete rows where 'id' is exactly 42
DELETE FROM users WHERE id 42 42

-- Delete all rows
DELETE FROM users

```

#### 5. System Commands

* `.commit`: **REQUIRED** to save changes. Flushes all dirty pages from memory to disk.
* `.tables`: Lists all tables in the database.
* `.schema <table>`: Shows the schema definition for a specific table.
* `.exit`: Closes the database and exits. **WARNING: Does not autosave.**

## 📂 File Format

TetoDB uses three types of binary files to store data:

* **`*.teto`**: The **Metadata/Catalog** file. Stores definitions of all tables, columns, and free lists (recycled row IDs).
* **`*_<table>.db`**: The **Heap File**. Stores the actual row data for a specific table.
* **`*_<table>_<col>.btree`**: The **Index File**. Stores the B+ Tree nodes (Internal and Leaf pages) for an indexed column.

## 🛠 Architecture

TetoDB is composed of several modular components:

1.  **Pager (`Pager.cpp`):** Handles low-level file I/O. It reads/writes 4KB blocks and manages the "Flush" strategy to persist data to disk.
2.  **B-Tree (`Btree.cpp`):** Implements a B+ Tree data structure for indexing. It supports splitting (for inserts) and merging (concepts for delete), ensuring the tree remains balanced.
3.  **Schema (`Schema.cpp`):** Defines the structure of tables (`Table`, `Column`, `Row`) and handles serialization/deserialization of row data into raw bytes.
4.  **Database Engine (`Database.cpp`):** Orchestrates the table metadata, manages the active tables, and executes high-level logic (e.g., deciding whether to use a full table scan or an index scan).
5.  **Command Parser (`CommandParser.cpp`):** Tokenizes and validates user input into structured command objects.

## 📊 Performance Benchmarks

TetoDB has been stress-tested with up to **10,000,000 rows**. Below are the results comparing the standard Linear Scan (No Index) vs. the B+ Tree Index.

### 1. The "Boss Fight" (10 Million Rows)

* **Dataset:** 10,000,000 records
* **Target:** Search for ID `8,000,000` (deep in the file)

| Metric | No Index (Linear Scan) | With Index (B-Tree) | Speedup |
| --- | --- | --- | --- |
| **SELECT Time** | `355.80 ms` | `0.19 ms` | **1,872x Faster** |
| **DELETE Time** | `334.09 ms` | `0.03 ms` | **11,136x Faster** |
| **Avg Insert** | `0.0004 ms` | `0.0017 ms` | *Slower (Overhead)* |

### 2. Time Growth Analysis (How it Scales)

As the database grows, the performance difference becomes drastic.

* **SELECT / DELETE ( vs ):**
* **Linear Scan:** Time grows **linearly**. 1M rows takes ~33ms, so 10M rows takes ~330ms.
* **B-Tree:** Time grows **logarithmically**. 1M rows takes 0.05ms, and 10M rows only grows to 0.19ms. It remains virtually instant regardless of size.


* **INSERT ( vs ):**
* **Linear Scan:** Consistently fast (~0.0004ms) because it simply appends data to the end of the file.
* **B-Tree:** Slightly slower (~0.0017ms) because it must traverse the tree to find the correct leaf node and occasionally split pages to keep the tree balanced.



| Dataset Size | Linear Select Time | B-Tree Select Time |
| --- | --- | --- |
| **100,000** | 3.34 ms | 0.04 ms |
| **1,000,000** | 33.67 ms | 0.05 ms |
| **10,000,000** | 355.80 ms | 0.19 ms |

## 🛠 Tools & Benchmarking

### Running the Benchmark Suite

TetoDB includes a Python script (`Benchmark.py`) that automates stress testing. It generates a script with `N` rows, runs it against both an indexed and non-indexed table, validates the data correctness, and generates a performance report.

**Usage:**

```bash
# Run a default test (50,000 rows)
python Benchmark.py

# Run a specific size (e.g., 1 million rows)
python Benchmark.py 1000000

```

### Inspecting the B-Tree Structure

(Optional) If you have the `BtreeVisualizer.py` tool, you can use it to inspect the internal hierarchy of your index files. This tool dumps the state of every node and verifies the integrity of the linked list connecting leaf nodes.

> **⚠️ NOTE: SMALL TESTS ONLY**
> This tool is designed for debugging small datasets. It has a safety limit of **1000 leaf pages** to prevent infinite loops. If you run this on a large database, it will likely report a **Cycle Error** or stop early.

**Usage:**

```bash
# Dump the internal structure of the B-Tree file
python BtreeVisualizer.py my_db_users_id.btree

```

**Output Example:**

```text
ROOT: 0 (Type: INTERNAL)

[Page 0] Type: INTERNAL, Parent: 0, Cells: 31
  -> Key: 297, Child: 2
  -> Key: 601, Child: 30
  ...

[Page 2] Type: LEAF, Parent: 0, Cells: 296
  -> Next Leaf: 30
  Keys: [1, 2, 3, ... 296]

...

--- Verifying Linked List Structure ---
Left-Most Leaf is Page 2. Walking the chain...
  Page 2 -> Page 30
  Page 30 -> Page 16
  ...
Walked 32 leaf pages.

```

## ⚠️ Limitations

* **No Comments Supported:** The parser does not handle comments (e.g., `#` or `--`) in script files or iterative mode. Each command must be in one **single line**. Lines must contain only **ONE** valid commands or be empty.
* **Strict Syntax:** Syntax validation is minimal. Commands must strictly follow the format shown above (e.g., correct number of arguments, proper quoting). Malformed commands may cause undefined behavior or crashes.
* **Fixed String Length:** Strings are strictly fixed-width (`char N`). If you insert a longer string, it is truncated.
* **Integer Keys Only:** B-Tree indexing is currently supported only for `int` columns.
* **Single User:** The database is not thread-safe and is designed for a single connection.

---

**Author:** duy-dustin-tong
**License:** MIT