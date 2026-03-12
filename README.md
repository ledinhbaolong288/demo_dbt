# DBT Demo Project - Tài liệu Demo DBT trên Docker

## Mục Lục
1. [Tổng Quan](#tổng-quan)
2. [Giới Thiệu DBT](#giới-thiệu-dbt-và-cơ-chế-hoạt-động)
3. [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
4. [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
5. [Cài Đặt và Khởi Động](#cài-đặt-và-khởi-động)
6. [Cấu Trúc Dữ Liệu](#cấu-trúc-dữ-liệu)
7. [Pipeline ETL](#pipeline-etl)
8. [Các Mô Hình DBT](#các-mô-hình-dbt)
9. [Data Quality Tests](#data-quality-tests)
10. [Kết Nối Với Các Data Warehouse](#kết-nối-với-các-data-warehouse)
11. [Hướng Dẫn Sử Dụng](#hướng-dẫn-sử-dụng)
    - [PostgreSQL](#2-truy-cập-postgresql-database)
    - [Oracle](#hướng-dẫn-sử-dụng-dbt-với-oracle-database)
    - [Redshift](#hướng-dẫn-sử-dụng-dbt-với-redshift)
    - [Trino](#hướng-dẫn-sử-dụng-dbt-với-trino)
12. [Docker Configuration](#docker-configuration)
13. [Workflow Tiêu Biểu](#workflow-tiêu-biểu)
14. [Khắc Phục Sự Cố](#khắc-phục-sự-cố)

---

## Tổng Quan

**DBT Demo Project** là một dự án mẫu xây dựng ETL pipeline với các công cụ:
- **DBT (Data Build Tool)**: Quản lý các transformation SQL
- **Database**: Cơ sở dữ liệu lưu trữ(Postgres, Redshift, Oracle...)
- **Docker & Docker Compose**: Containerization và orchestration
- **Python**: Script load dữ liệu từ JSON

### Mục Đích
Dự án này minh họa:
- Cách setup pipeline ETL hoàn chỉnh
- Các layer dữ liệu (Raw → Staging → Mart)
- Data quality testing với dbt
- Công cụ data modeling hiện đại

---

## Cấu Trúc Dự Án

```
.
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── main.py                     # Python script for data loading
├── profiles.yml                # DBT connection configuration
├── note.txt                    # Project notes and commands
├── Data_src/                   # Source data in JSON format
│   ├── orders.json            # Orders raw data
│   └── users.json             # Users raw data
└── dbt_demo/                   # Main DBT project
    ├── dbt_project.yml        # DBT project configuration
    ├── logs/                  # DBT execution logs
    ├── models/                # SQL transformation models
    │   ├── schema.yml         # Model definitions and tests
    │   ├── staging/           # Raw data staging models
    │   │   ├── stg_orders.sql # Staging for orders
    │   │   └── stg_users.sql  # Staging for users
    │   └── marts/             # Business logic models
    │       └── fct_orders.sql # Fact table for orders
    ├── tests/                 # Custom data quality tests
    │   └── order_amount_positive.sql
    └── target/                # Generated artifacts
        ├── compiled/          # Compiled SQL files
        ├── run/              # Executed run results
        ├── manifest.json     # DBT metadata
        └── run_results.json  # Execution results
```

---

## Yêu Cầu Hệ Thống

### Bắt Buộc
- **Docker Desktop**: Version 20.10 trở lên
- **Docker Compose**: Version 1.29 trở lên
- **Git**: Để clone hoặc version control

### Cấu Hình Tối Thiểu
- RAM: 4GB
- Disk space: 5GB
- CPU: 2 cores

### Ports Cần Mở
- **5432**: PostgreSQL database
- **5439**: Amazon Redshift
- **1521**: Oracle
- **8080, 8443**: Trino
---

## Giới Thiệu DBT và Cơ Chế Hoạt Động

### DBT là gì?

**dbt (Data Build Tool)** là công cụ quản lý phần **transformation** (T) của ETL pipeline. Thay vì viết các stored procedures phức tạp hay orchestration scripts, dbt cho phép bạn:

- Viết transformation bằng **SQL thuần tuý** (hoặc Python)
- Quản lý dependencies giữa models tự động
- Chạy từ **command-line** (dbt Core) hoặc **web UI** (dbt Cloud)
- Thực hiện **data quality testing** tích hợp
- Tạo **documentation** tự động từ code
- **Version control** toàn bộ transformation pipeline

### Sơ Đồ Cơ Chế DBT Hoạt Động

```
┌─────────────────────────────────────────────────────────┐
│                   DATA SOURCES                          │
│  (JSON, CSV, APIs, Databases, Data Lakes)               │
└───────────────┬─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────┐
│         DBT PARSING & COMPILATION                       │
│  • Read .sql + .yml models                              │
│  • Parse Jinja2 templates                               │
│  • Build dependency graph (DAG)                         │
│  • Compile SQL for target database                      │
└───────────────┬─────────────────────────────────────────┘
                │
                ▼
        ┌───────┴───────┐
        │               │
        ▼               ▼
   ┌─────────┐      ┌────────┐
   │  RAW /  │      │ STAGING│
   │ SOURCES │      │ LAYER  │
   └─────────┘      └────────┘
        │               │
        └───────┬───────┘
                ▼
        ┌──────────────────┐
        │ INTERMEDIATE     │
        │ LAYER (Optional) │
        └───────┬──────────┘
                │
                ▼
        ┌──────────────────┐
        │  MART / FACT     │
        │  LAYER           │
        └───────┬──────────┘
                │
                ▼
       ┌────────────────────┐
       │   DBT EXECUTION    │
       │  • Run models      │
       │  • Run tests       │
       │  • Generate docs   │
       └─────────┬──────────┘
                │
                ▼
    ┌──────────────────────────┐
    │  WAREHOUSE / LAKEHOUSE   │
    │  (PostgreSQL, Redshift,  │
    │   Oracle, Trino)         │
    └──────────────────────────┘
                │
                ▼
    ┌──────────────────────────┐
    │  BI TOOLS & ANALYTICS    │
    │  (Tableau, Power BI,     │
    │   Looker, SQL queries)   │
    └──────────────────────────┘
```

### Chi Tiết Các Giai Đoạn Hoạt Động

**Phase 1: Parsing & Compilation**
```
Input: models/*.sql, dbt_project.yml, profiles.yml
              ↓
        Parse Jinja2 template
            ({{ ref() }})
              ↓
  Build Directed Acyclic Graph (DAG)
              ↓
        Compile to SQL
              ↓
Output: Compiled SQL files (target/compiled/)
```

**Phase 2: Execution**
```
$ dbt run

Execute models in dependency order:
  ✓ stg_users (no dependencies)
  ✓ stg_orders (no dependencies)
  ✓ fct_orders (depends on stg_users, stg_orders)

Result: Models created/updated in warehouse
```

**Phase 3: Testing**
```
$ dbt test

Run all tests defined in schema.yml:
  ✓ Test: stg_users.user_id not null
  ✓ Test: stg_users.user_id unique
  ✓ Test: stg_orders.order_id not null
  ✓ Test: fct_orders.user_id relationships
  ✓ Test: custom order_amount_positive

Result: PASS (if all tests pass) or FAIL (if any tests fail)
```

**Phase 4: Documentation**
```
$ dbt docs generate

Generate:
  • docs/index.html
  • Data lineage diagram (DAG)
  • Model descriptions & tests
  • Column-level documentation

$ dbt docs serve → Open browser to http://localhost:8000
```

### Ví Dụ Thực Tế: Chạy `dbt build` 

```bash
$ docker compose exec dbt dbt build

# Output:
Running with dbt=1.5.0
Found 3 models, 5 tests, 0 snapshots, 0 analyses, 0 macros, 0 operations, 0 seed files, 0 sources

13:45:20  Running 1 of 3 START table model dbt_demo.stg_users
13:45:21  Running 1 of 3 PASS table model dbt_demo.stg_users [CREATE TABLE 0.50s]

13:45:21  Running 2 of 3 START table model dbt_demo.stg_orders
13:45:22  Running 2 of 3 PASS table model dbt_demo.stg_orders [CREATE TABLE 0.45s]

13:45:22  Running 3 of 3 START table model dbt_demo.fct_orders
13:45:23  Running 3 of 3 PASS table model dbt_demo.fct_orders [CREATE TABLE 0.38s]

13:45:24  Running 1 of 5 START test not_null_stg_users_user_id
13:45:24  Running 1 of 5 PASS test not_null_stg_users_user_id [PASSED 0.12s]

13:45:24  Running 2 of 5 START test unique_stg_users_user_id
13:45:24  Running 2 of 5 PASS test unique_stg_users_user_id [PASSED 0.10s]

13:45:25  Running 3 of 5 START test not_null_stg_orders_order_id
13:45:25  Running 3 of 5 PASS test not_null_stg_orders_order_id [PASSED 0.11s]

13:45:25  Running 4 of 5 START test relationships_fct_orders_user_id__user_id__ref__stg_users
13:45:25  Running 4 of 5 PASS test relationships_fct_orders_user_id__user_id__ref__stg_users [PASSED 0.15s]

13:45:26  Running 5 of 5 START test order_amount_positive
13:45:26  Running 5 of 5 PASS test order_amount_positive [PASSED 0.08s]

13:45:26  Finished running 3 models, 5 tests in 6.23s.

# ✓ Kế quả: 3 models được build thành công, 5 tests đều PASS
# Điều này cho thấy:
#  - Tất cả models được tạo thành công
#  - Không có lỗi syntax hoặc runtime
#  - Dữ liệu đáp ứng mọi yêu cầu data quality
```

### Key Concepts

| Concept | Mô Tả | Ví Dụ |
|---------|-------|-------|
| **Model** | File .sql chứa SELECT query | stg_orders.sql, fct_orders.sql |
| **Materialization** | Cách lưu model (VIEW, TABLE, ...) | staging = VIEW, marts = TABLE |
| **ref()** | Reference giữa models | `{{ ref('stg_orders') }}` |
| **source()** | Reference đến raw data | `{{ source('raw', 'orders_raw') }}` |
| **Jinja2** | Template language trong dbt | `{% if execute %}...{% endif %}` |
| **Test** | Data quality validation | not_null, unique, relationships |
| **DAG** | Dependency graph (visual) | stg_users → fct_orders ← stg_orders |
| **Seed** | CSV → Table (static data) | Lookup tables, dimension tables |

### Lợi Ích Chính của dbt

✅ **SQL Development** - Lập trình transformation bằng SQL thuần, không cần PRO  
✅ **Version Control** - Git control cho tất cả transformations  
✅ **Testing** - Built-in data quality checks tự động  
✅ **Documentation** - Auto-generated docs từ code + descriptions  
✅ **Modularity** - Reuse models, macros, tests dễ dàng  
✅ **Lineage** - Visual DAG hiển thị dependencies  
✅ **Performance** - Parallel execution, incremental builds  
✅ **Debugging** - Debug mode, compiled SQL inspection  

---

## Cài Đặt và Khởi Động

### 1. Chuẩn Bị Môi Trường

```bash
# Copy file hiện tại về thư mục làm việc
cd \Demo\demo_dbt

# Chuẩn bị các package install trên file Dockerfile
- dbt-postgres     : Thư viện adapter dbt cho PostgreSQL
- dbt-redshift     : Thư viện adapter dbt cho Redshift
- dbt-oracle       : Thư viện adapter dbt cho oracle
- dbt-trino        :Thư viện adapter dbt cho trino
# - psycopg2-binary  : Thư viện kết nối Python với PostgreSQL
# - python-dotenv    : Thư viện đọc environment variables

# Kiểm tra Docker đang chạy
docker --version
# Output mong đợi:
# Docker version 20.10.0, build ABC123

docker compose --version
# Output mong đợi:
# Docker Compose version 2.0.0, build EFG789
```

**✓ Yêu cầu thành công nếu:** Cả 2 commands trả về phiên bản

### 2. Khởi Động Services

```bash
# Build image và khởi động services
docker compose up -d --build

# Output:
# Building dbt
# ...
# Creating postgres-dbt ... done
# Creating dbt-postgres  ... done
```

**✓ Yêu cầu thành công nếu:** Processing finished without errors

```bash
# Xác nhận services đã chạy
docker compose ps

# Output mong đợi:
# CONTAINER ID   IMAGE              NAMES          STATUS
# a1b2c3d4e5f6   postgres:15        postgres-dbt   Up 1 minute
# f6e5d4c3b2a1   dbt-postgres       dbt-postgres   Up 1 minute

# ✓ Hay: Cả 2 containers STATUS = "Up X minutes"
# ✗ Sai: STATUS = "Exited (X)" hoặc "Created"
```

### 3. Load Dữ Liệu Ban Đầu

```bash
# Chạy Python script để tạo bảng raw và load dữ liệu
docker compose exec dbt python /workspace/main.py

# Output thành công:
# Connected to database: analytics
# Creating raw schema...
# Creating tables:
#   - raw.orders_raw
#   - raw.users_raw
# Truncating existing data...
# Loading data from Data_src/orders.json...
# Inserted 150 orders into raw.orders_raw
# Loading data from Data_src/users.json...
# Inserted 50 users into raw.users_raw
# Data loading completed successfully!

# ✓ Yêu cầu thành công: "Data loading completed successfully!" xuất hiện
# ✗ Sai: Lỗi "Connection refused" hoặc "File not found"
```

### 4. Chạy DBT Pipeline

```bash
# Thực hiện toàn bộ pipeline (build models + run tests)
docker compose exec dbt dbt build

# Output:
# Running with dbt=1.5.0
# Found 3 models, 5 tests, 0 snapshots, 0 analyses
# 
# 13:45:20  Running 1 of 3 START table model dbt_demo.stg_users
# 13:45:21  Running 1 of 3 PASS table model dbt_demo.stg_users [CREATE TABLE 0.50s]
#
# 13:45:21  Running 2 of 3 START table model dbt_demo.stg_orders
# 13:45:22  Running 2 of 3 PASS table model dbt_demo.stg_orders [CREATE TABLE 0.45s]
#
# 13:45:22  Running 3 of 3 START table model dbt_demo.fct_orders
# 13:45:23  Running 3 of 3 PASS table model dbt_demo.fct_orders [CREATE TABLE 0.38s]
#
# 13:45:24  Running test not_null_stg_users_user_id ...
# 13:45:24  PASS [PASSED 0.12s]
#
# 13:45:24  Running test unique_stg_users_user_id ...
# 13:45:24  PASS [PASSED 0.10s]
#
# 13:45:25  Running test order_amount_positive ...
# 13:45:25  PASS [PASSED 0.08s]
#
# 13:45:26  Finished running 3 models, 5 tests in 6.23s.

# ✓ Yêu cầu thành công:
#   - "PASS" xuất hiện cho mỗi model
#   - "Finished running 3 models, 5 tests"
#   - Không có lỗi (error output)
#
# ✗ Sai:
#   - "FAIL" xuất hiện
#   - "Error" messages
#   - "Connection refused"
```

**Hoặc chạy riêng từng phần:**

```bash
# Chỉ build models (không run tests)
docker compose exec dbt dbt run
# Expected output: "Finished running 3 models"

# Chỉ chạy tests (không run models)
docker compose exec dbt dbt test
# Expected output: "Finished running 5 tests" (all PASS)

# Tạo snapshots (nếu có)
docker compose exec dbt dbt snapshot
# Expected output: "Snapshot completed" hoặc "no snapshots to execute"
```



---

## Cấu Trúc Dữ Liệu

### Data Flow Diagram
```
JSON Files
    ↓
main.py (Python ETL)
    ↓
raw schema (PostgreSQL)
    ├── raw.orders_raw
    └── raw.users_raw
    ↓
DBT Staging Layer (stg_*)
    ├── dbt_dev.stg_orders
    └── dbt_dev.stg_users
    ↓
DBT Mart Layer (fct_*)
    └── dbt_dev.fct_orders
    ↓
Analytics Ready Tables
```

### Raw Tables (raw schema)

#### raw.orders_raw
Chứa dữ liệu đơn hàng nguyên bản từ JSON

| Column | Type | Mô Tả |
|--------|------|-------|
| order_id | bigint | ID đơn hàng (PK) |
| user_id | bigint | ID người dùng (FK) |
| total_amount | numeric(18,2) | Tổng giá trị đơn hàng |
| created_at | timestamp | Ngày tạo đơn hàng |
| etl_time | timestamp | Timestamp load dữ liệu |

#### raw.users_raw
Chứa dữ liệu người dùng nguyên bản từ JSON

| Column | Type | Mô Tả |
|--------|------|-------|
| user_id | bigint | ID người dùng (PK) |
| user_name | text | Tên người dùng |
| email | text | Email |
| created_at | timestamp | Ngày tạo tài khoản |
| updated_at | timestamp | Ngày cập nhật cuối |
| etl_time | timestamp | Timestamp load dữ liệu |

---

## Pipeline ETL

### Python Data Loading (main.py)

Script `main.py` thực hiện các bước:

1. **Kết nối Database**
   ```python
   DB_CONFIG = {
       "host": "DB_HOST",
       "port": "DB_PORT",
       "dbname": "DB_DBNAME",
       "user": "user",
       "password": "password",
   }
   ```

2. **Tạo Raw Schema và Tables**
   - Tạo schema `raw` nếu chưa tồn tại
   - Tạo bảng `raw.orders_raw` 
   - Tạo bảng `raw.users_raw`

3. **Xóa Dữ Liệu Cũ**
   ```python
   truncate_raw_tables(conn)  # Xóa bảng trước load
   ```

4. **Load Dữ Liệu từ JSON**
   - Đọc `Data_src/orders.json`
   - Đọc `Data_src/users.json`
   - Insert vào raw tables

5. **Commit và Đóng Kết Nối**

### DBT Transformation

DBT xử lý logic transformation từ raw data → analytics-ready tables.

---

## Các Mô Hình DBT

### 1. Staging Models (dbt_dev.stg_*)

Lớp staging làm sạch và chuẩn hóa dữ liệu từ raw tables. Đây là bước trung gian giúp:
- Chuẩn hóa kiểu dữ liệu
- Loại bỏ dữ liệu không cần thiết
- Áp dụng single responsibility principle

#### stg_orders.sql

**Mục đích của model này:**
Model này thực hiện các công việc sau:
1. **Type casting**: Chuyển đổi các cột sang kiểu dữ liệu chính xác (bigint, numeric, timestamp)
2. **Standardization**: Chuẩn hóa naming convention
3. **Preparation**: Chuẩn bị dữ liệu cho các model phía sau

```sql
-- Model stg_orders: Staging layer cho orders
-- Tác dụng: Chuẩn hóa và làm sạch dữ liệu orders từ raw
-- Input: raw.orders_raw
-- Output: Cleaned orders table / view

select
    cast(order_id as bigint) as order_id,                    -- ID đầu tiên
    cast(user_id as bigint) as user_id,                      -- FK tới users
    cast(total_amount as numeric(18,2)) as total_amount,     -- Định dạng tiền tệ
    cast(created_at as timestamp) as created_at,             -- Timestamp
    cast(etl_time as timestamp) as etl_time                  -- Khi load
from raw.orders_raw
```

**Materialization:** VIEW (được cấu hình trong dbt_project.yml)
- Ưu điểm: Tiết kiệm storage, luôn cập nhật
- Nhược điểm: Query chậm hơn so với TABLE

**Input / Output:**
- Input: raw schema có table `raw.orders_raw` với 150 rows
- Output: `dbt_dev.stg_orders` gồm 150 rows với cột được cast đúng kiểu

#### stg_users.sql

**Mục đích của model này:**
Model này thực hiện các công việc:
1. **Text cleaning**: Trim spaces, normalize email
2. **Type casting**: Cast kiểu dữ liệu
3. **Normalization**: Chuyển email thành lowercase

```sql
-- Model stg_users: Staging layer cho users
-- Tác dụng: Chuẩn hóa, làm sạch dữ liệu users từ raw
-- Input: raw.users_raw
-- Output: Cleaned users table / view

select
    cast(user_id as bigint) as user_id,
    trim(user_name) as user_name,                    -- Loại bỏ spaces
    lower(trim(email)) as email,                     -- Normalize email
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at,
    cast(etl_time as timestamp) as etl_time
from raw.users_raw
```

**Materialization:** VIEW

**Input / Output:**
- Input: `raw.users_raw` gồm 50 rows
- Output: `dbt_dev.stg_users` gồm 50 rows sau khi trim và normalize

---

### 2. Mart Models (dbt_dev.fct_*)

Lớp mart chứa business logic tổng hợp, sẵn sàng cho analytics. Đây là bước cuối cùng trước khi dữ liệu được sử dụng bởi BI tools.

#### fct_orders.sql

**Mục đích của model này:**
Model này thực hiện các công việc sau:
1. **Data enrichment**: Join dữ liệu from 2 source
2. **Business context**: Thêm thông tin user vào orders
3. **Analytics ready**: Format cho BI tools

```sql
-- Model fct_orders: Fact table cho analytics
-- Tác dụng: Kết hợp orders + users thông tin, sẵn sàng cho BI
-- Input: stg_orders, stg_users
-- Output: Fact table với context dầy đủ

select
    o.order_id,                          -- Order ID
    o.user_id,                           -- User ID để join
    u.user_name,                         -- Enriched: User name
    u.email,                             -- Enriched: User email
    o.total_amount,                      -- Order amount
    o.created_at                         -- Order creation date
from {{ ref('stg_orders') }} o           -- Reference stg_orders model
left join {{ ref('stg_users') }} u       -- Reference stg_users model
    on o.user_id = u.user_id             -- Join condition
```

**Đặc điểm:**
- Sử dụng **Jinja2 macros** `{{ ref() }}` để tham chiếu models
- dbt tự động theo dõi dependency: fct_orders depends on stg_orders + stg_users
- Khi stg_orders hoặc stg_users thay đổi, fct_orders tự động rebuild

**Materialization:** TABLE (được cấu hình trong dbt_project.yml)
- Ưu điểm: Query nhanh, có index support
- Nhược điểm: Tốn storage, cập nhật chậm

**Input / Output:**
- Input: 150 orders left join với 50 users
- Output: `dbt_dev.fct_orders` gồm 150 rows (full customer detail)



---

## Data Quality Tests

DBT tích hợp data quality validations thông qua `schema.yml`. Tests giúp đảm bảo dữ liệu đáp ứng các yêu cầu business.

### Configuration (schema.yml)

```yaml
# Định nghĩa models và tests
# Tác dụng: Validate dữ liệu đáp ứng quality standards
version: 2

models:
  - name: stg_orders
    columns:
      - name: order_id
        tests:
          - not_null    # Kiểm tra: không có giá trị NULL
          - unique      # Kiểm tra: không có bản ghi trùng lặp
      
      - name: user_id
        tests:
          - not_null
          - relationships:  # Kiểm tra: FK constraint
              to: ref('stg_users')
              field: user_id
      
      - name: total_amount
        tests:
          - not_null

  - name: stg_users
    columns:
      - name: user_id
        tests:
          - not_null
          - unique
      
      - name: user_name
        tests:
          - not_null
          - unique
      
      - name: email
        tests:
          - not_null
          - unique

  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - not_null
          - unique
          - relationships:
              to: ref('stg_orders')
              field: order_id
      
      - name: user_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_users')
              field: user_id
      
      - name: total_amount
        tests:
          - not_null
```

### Built-in Tests và Cách Hoạt Động

| Test | Mô Tả | Ví Dụ | Output |
|------|-------|-------|--------|
| `not_null` | Kiểm tra NULL values | Tất cả `user_id` phải có giá trị | ✓ PASS: 0 NULL rows |
| `unique` | Kiểm tra duplicate values | Không được có 2 `user_id` giống | ✓ PASS: Tất cả unique |
| `relationships` | Kiểm tra FK constraint | `order_id` phải tồn tại trong `stg_orders` | ✓ PASS: Tất cả FK references valid |
| `accepted_values` | Kiểm tra giá trị trong list | Status ∈ [pending, completed, cancelled] | ✓ PASS: Tất cả values trong list |

### Ví Dụ Khi Chạy `dbt test`

**Scenario 1: TẤT CẢ TESTS PASS ✓**

```bash
$ docker compose exec dbt dbt test

# Output:
Running with dbt=1.5.0
Found 3 models, 5 tests

13:45:24  Running test not_null_stg_users_user_id ...
13:45:24  PASS [PASSED 0.12s]

13:45:24  Running test unique_stg_users_user_id ...
13:45:24  PASS [PASSED 0.10s]

13:45:25  Running test not_null_stg_orders_order_id ...
13:45:25  PASS [PASSED 0.11s]

13:45:25  Running test relationships_fct_orders_user_id__user_id__ref__stg_users ...
13:45:25  PASS [PASSED 0.15s]

13:45:26  Running test order_amount_positive ...
13:45:26  PASS [PASSED 0.08s]

13:45:26  Finished running 5 tests in 0.62s.

# ✓ YÊU CẦU THÀNH CÔNG:
#   - Tất cả tests = "PASS"
#   - "Finished running 5 tests" cuối cùng
#   - Không có lỗi hoặc cảnh báo
```

**Scenario 2: TEST FAIL ✗ (do dữ liệu lỗi)**

```bash
$ docker compose exec dbt dbt test

# Output:
13:45:24  Running test not_null_stg_users_user_id ...
13:45:24  FAIL [FAILED 0.15s]

13:45:24  Running test unique_stg_users_user_id ...
13:45:24  FAIL [FAILED 0.12s]

# Details:
Compiled Code:
select *
from stg_users
where user_id is null

Failure Details:
Found 5 rows which violated the constraint user_id IS NOT NULL

# ✗ VẤN ĐỀ:
#   - 5 rows có user_id = NULL
#   - Cần kiểm tra dữ liệu source raw.users_raw
#   - Cần fix validation logic
```

**Scenario 3: RELATIONSHIP TEST FAIL ✗ (FK mismatch)**

```bash
13:45:25  Running test relationships_fct_orders_user_id__user_id__ref__stg_users ...
13:45:25  FAIL [FAILED 0.18s]

Compiled Code:
select *
from fct_orders
where user_id not in (select user_id from stg_users)

Failure Details:
Found 3 rows with user_id values that don't exist in stg_users

# ✗ VẤN ĐỀ:
#   - 3 orders có user_id không tồn tại trong users table
#   - Cần xóa orphan orders hoặc thêm missing users
#   - Data integrity issue cần sửa ở data source
```

### Custom Tests (order_amount_positive.sql)

**Mục đích của test này:**
Test này kiểm tra rằng tất cả đơn hàng có giá trị > 0. Đây là validation dành riêng cho business logic.

```sql
-- Custom Test: order_amount_positive
-- Tác dụng: Ensure all orders có giá trị dương (> 0)
-- Logic: Query trả về tất cả rows vi phạm constraint

select *
from {{ ref('fct_orders') }}
where total_amount <= 0
```

**Cách hoạt động:**
- Nếu query trả về **0 rows** → Test **PASS** ✓
  - Điều này có nghĩa: Tất cả order amounts > 0
- Nếu query trả về **records** → Test **FAIL** ✗
  - Ví dụ: 2 rows có total_amount = 0 hoặc negative
  - Cần debug và fix data source

**Output thành công:**

```bash
13:45:26  Running test order_amount_positive ...
13:45:26  PASS [PASSED 0.08s]

# Vô hiệu: Không có orders có total_amount <= 0
```

**Output thất bại:**

```bash
13:45:26  Running test order_amount_positive ...
13:45:26  FAIL [FAILED 0.12s]

Failure Details:
Found 2 rows which violated the constraint total_amount > 0

# Các row bị lỗi:
order_id | user_id | total_amount | issue
---------|---------|--------------|-------
1005     | 25      | 0            | Negative amount
1008     | 32      | -150.00      | Refund not processed correctly
```

---

---

## Kết Nối Với Các Data Warehouse

DBT hỗ trợ nhiều loại data warehouse khác nhau thông qua các adapter khác nhau. Dưới đây là hướng dẫn kết nối với các platform phổ biến.

### 1. DBT + Oracle Database

**Cài đặt Adapter Oracle**

```bash
# Install dbt-oracle adapter
pip install dbt-oracle

# Kiểm tra cài đặt
dbt --version
# Output mong đợi: dbt-core version X.Y.Z, + oracle plugin
```

**Cấu Hình profiles.yml**

```yaml
# profiles.yml - Cấu hình kết nối DBT tới Oracle Database
# Tác dụng: Cung cấp thông tin connection để dbt kết nối tới Oracle

oracle_demo:
  target: dev
  outputs:
    dev:
      type: oracle                     # Database adapter type
      host: oracle.example.com         # Oracle hostname hoặc IP
      port: 1521                       # Oracle port (default: 1521)
      user: dbt_user                   # Oracle username
      password: your_password          # Oracle password
      service_name: ORCL              # Oracle service name (hoặc SID)
      schema: dbt_dev                  # Schema để tạo models
      threads: 4                       # Parallel threads
      
      # Optional settings
      tablespace: users                # Tablespace cho bảng
      protocol: tcp                    # Connection protocol
```

**dbt_project.yml - Sử dụng Profile**

```yaml
name: "dbt_demo"
version: "1.0"
config-version: 2

profile: "oracle_demo"    # Tham chiếu tới profile trong profiles.yml

# Model configuration
models:
  dbt_demo:
    staging:
      +materialized: view        # VIEWs cho staging
    marts:
      +materialized: table       # TABLEs cho marts
```

**Test Kết Nối**

```bash
# Test connection
dbt debug

# Output mong đợi:
```
dbt version: 1.5.0
python version: 3.10.0
Connection:
  type: oracle
  host: oracle.example.com
  user: dbt_user
  password: [REDACTED]
  port: 1521
  service_name: ORCL
  schema: dbt_dev
  state: Open

# ✓ Yêu cầu thành công: "state: Open"
# ✗ Sai: "state: Closed" hoặc "Connection refused"
```
```

**Chạy Pipeline trên Oracle**

```bash
# Parse project
dbt parse

# Run models
dbt run

# Output:
# Running with dbt=1.5.0
# Found 3 models, 5 tests
# 
# Running 1 of 3 PASS stg_users ...
# Running 2 of 3 PASS stg_orders ...
# Running 3 of 3 PASS fct_orders ...
# Finished running 3 models

# ✓ Yêu cầu thành công: Models được tạo trên Oracle schema dbt_dev
```

**Kiểm Tra Models trên Oracle**

```sql
-- Kết nối tới Oracle và kiểm tra
SELECT * FROM dbt_dev.stg_users;        -- Xem staging models
SELECT * FROM dbt_dev.fct_orders;       -- Xem fact tables

-- Số lượng từng bảng
SELECT COUNT(*) FROM dbt_dev.stg_users;      -- Expected: 50
SELECT COUNT(*) FROM dbt_dev.stg_orders;     -- Expected: 150
SELECT COUNT(*) FROM dbt_dev.fct_orders;     -- Expected: 150
```

---

### 2. DBT + Amazon Redshift

**Cài đặt Adapter Redshift**

```bash
# Install dbt-redshift adapter
pip install dbt-redshift

# Kiểm tra cài đặt
dbt --version
# Output: dbt-core version X.Y.Z, + redshift plugin
```

**Cấu Hình profiles.yml**

```yaml
# profiles.yml - Cấu hình kết nối DBT tới Redshift
# Tác dụng: Kết nối tới AWS Redshift cluster

redshift_demo:
  target: dev
  outputs:
    dev:
      type: redshift                              # Redshift adapter
      host: dbt-redshift-cluster.abc123.us-east-1.redshift.amazonaws.com
      port: 5439                                  # Redshift port
      user: admin                                 # Redshift master user
      password: your_password
      dbname: analytics                           # Database name
      schema: dbt_dev                             # Schema
      threads: 4
      
      # Redshift-specific settings
      connect_timeout: 30                         # Connection timeout
      ra3_node: false                             # RA3 node tối ưu hóa
      
      # IAM Authentication (optional, more secure)
      # iam: true
      # cluster_id: dbt-redshift-cluster
      # region: us-east-1
```

**Ưu Điểm Redshift**

- Tối ưu cho analytical queries lớn
- MPP (Massively Parallel Processing) architecture
- Rẻ hơn so với data warehouse khác
- Tích hợp tốt với AWS services

**Test Kết Nối Redshift**

```bash
$ dbt debug

# Output:
Connection:
  type: redshift
  host: dbt-redshift-cluster.abc123.us-east-1.redshift.amazonaws.com
  port: 5439
  user: admin
  state: Open

# ✓ Yêu cầu thành công: "state: Open"
```

**Chạy Pipeline trên Redshift**

```bash
# Build models
dbt run

# Output mong đợi:
Running 1 of 3 START table model dbt_demo.stg_users
Running 1 of 3 PASS table model dbt_demo.stg_users [CREATE TABLE 5.23s]

# Note: Redshift thường chậm hơn PostgreSQL vì cần compile trên MPP
# Thời gian xử lý lâu hơn là bình thường
```

**Redshift-Specific Features**

```sql
-- Kiểm tra bảng trên Redshift
SELECT * FROM dbt_dev.stg_users;

-- Xem dung lượng bảng
SELECT schemaname, tablename, size
FROM svv_table_info
WHERE schemaname = 'dbt_dev';

-- Xem query performance
SELECT query, starttime, duration
FROM stl_query
WHERE userid > 1
ORDER BY starttime DESC
LIMIT 10;
```

---

### 3. DBT + Trino (PrestoSQL)

**Cài Đặt Adapter Trino**

```bash
# Install dbt-trino adapter
pip install dbt-trino

# Kiểm tra cài đặt
dbt --version
# Output: dbt-core version X.Y.Z, + trino plugin
```

**Cấu Hình profiles.yml**

```yaml
# profiles.yml - Cấu hình kết nối DBT tới Trino
# Tác dụng: Kết nối tới Trino cluster (distributed SQL engine)

trino_demo:
  target: dev
  outputs:
    dev:
      type: trino                        # Trino adapter
      host: trino-coordinator.example.com  # Trino coordinator node
      port: 8080                         # Trino port
      user: dbt_user                     # Trino user
      password: your_password            # Trino password (nếu auth enabled)
      database: hive                     # Trino catalog (e.g., hive, iceberg)
      schema: dbt_dev                    # Schema trong catalog
      threads: 4
      
      # Trino-specific settings
      timeout_seconds: 300               # Query timeout
      
      # For Kerberos authentication
      # krb5_config_path: /etc/krb5.conf
      
      # For SSL/TLS
      # ssl: true
      # ca_path: /path/to/ca.pem
```

**Trino Catalogs (Backends)**

Trino có thể kết nối tới nhiều data sources khác nhau:

```yaml
# Ví dụ: Trino kết nối tới Hive + Iceberg + PostgreSQL

trino_demo:
  outputs:
    dev:
      type: trino
      host: trino-coordinator.example.com
      port: 8080
      
      # Sử dụng Hive catalog
      database: hive                     # Hive metastore
      schema: dbt_dev
      
      # Hoặc sử dụng Iceberg catalog (modern format)
      # database: iceberg
      
      # Hoặc sử dụng PostgreSQL connector
      # database: postgres
```

**Test Kết Nối Trino**

```bash
$ dbt debug

# Output:
Connection:
  type: trino
  host: trino-coordinator.example.com
  port: 8080
  user: dbt_user
  database: hive
  schema: dbt_dev
  state: Open

# ✓ Yêu cầu thành công: "state: Open"
```

**Chạy Pipeline trên Trino**

```bash
# Build models
dbt run

# Output:
Running with dbt=1.5.0
Found 3 models, 5 tests

Running 1 of 3 START table model dbt_demo.stg_users
Running 1 of 3 PASS table model dbt_demo.stg_users [CREATE TABLE USING ICEBERG 8.45s]

Running 2 of 3 START table model dbt_demo.stg_orders
Running 2 of 3 PASS table model dbt_demo.stg_orders [CREATE TABLE USING ICEBERG 7.23s]

Running 3 of 3 START table model dbt_demo.fct_orders
Running 3 of 3 PASS table model dbt_demo.fct_orders [CREATE TABLE USING ICEBERG 6.12s]

Finished running 3 models in 22.1s

# ✓ Yêu cầu thành công: Models tạo thành công trên Trino
```

**Trino-Specific Features**

```sql
-- Kiểm tra bảng trên Trino
SELECT * FROM hive.dbt_dev.stg_users;

-- Xem metadata
SELECT * FROM system.metadata.table_comments
WHERE table_schema = 'dbt_dev';

-- Xem tất cả tables trong schema
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'dbt_dev';
```

**So Sánh Các Data Warehouse**

| Tính Năng | PostgreSQL | Oracle | Redshift | Trino |
|-----------|-----------|--------|----------|-------|
| **Thiết lập** | Dễ (local) | Phức tạp | Medium (AWS) | Medium |
| **Chi phí** | Miễn phí | Cao | Medium | Thấp (open-source) |
| **Hiệu năng** | Tốt | Tốt | Xấu hơn (MPP) | Tùy backend |
| **Scalability** | Vertical | Vertical | Horizontal (MPP) | Horizontal |
| **Use Case** | Dev/Testing | Enterprise | Big data | Multi-source federated |
| **dbt Support** | ✅ Tốt | ✅ Tốt | ✅ Tốt | ✅ Tốt |

### Chuyển Đổi Giữa Data Warehouses

Để chuyển DBT project từ PostgreSQL sang warehouse khác:

1. **Cập nhật profiles.yml**
   ```yaml
   # Thay đổi database type, host, port, credentials
   type: redshift  # hoặc oracle, trino
   ```

2. **Cập nhật dbt_project.yml**
   ```yaml
   profile: "redshift_demo"  # Tham chiếu tới profile mới
   ```

3. **Kiểm tra SQL compatibility**
   ```bash
   dbt parse  # Validate syntax trên new warehouse
   dbt debug  # Test connection
   ```

4. **Test models**
   ```bash
   dbt run --select stg_users  # Run single model first
   dbt test                    # Run all tests
   ```

---

## Hướng Dẫn Sử Dụng

### 1. Kiểm Tra Status Services

```bash
# Xem services status
docker compose ps

# Xem logs của containers
docker compose logs -f
docker compose logs -f dbt
docker compose logs -f postgres
```

### 2. Truy Cập PostgreSQL Database

#### Cách 1: Dùng psql CLI
```bash
# Kết nối vào PostgreSQL
docker exec -it postgres-dbt psql -U postgres -d analytics

# Các lệnh psql hữu ích:
\dn                              # List tất cả schemas
\dt                              # List tất cả tables
\dt raw.*                        # List tables trong raw schema
\dt dbt_dev.*                    # List tables trong dbt_dev schema
\d raw.orders_raw               # Chi tiết cột của orders_raw table
```

#### Cách 2: Kết nối với DBeaver/IDE
- **Host:** localhost
- **Port:** 5432
- **Username:** 
- **Password:**
- **Database:**

### 3. Truy Vấn Dữ Liệu

```sql
-- Kiểm tra dữ liệu raw
select * from raw.orders_raw;
select * from raw.users_raw;

-- Kiểm tra dữ liệu staging
select * from dbt_dev.stg_orders;
select * from dbt_dev.stg_users;

-- Kiểm tra dữ liệu mart
select * from dbt_dev.fct_orders;

-- Thống kê
select count(*) from raw.orders_raw;
select count(distinct user_id) from raw.users_raw;
```

### 4. Chạy DBT Commands

```bash
# Develop mode - chạy trong dbt container
docker compose exec dbt bash

# Trong dbt container:

# Parse project (validate syntax)
dbt parse

# Run models
dbt run

# Run tests
dbt test

# Build (run + test)
dbt build

# Generate documentation
dbt docs generate

# Tạo freshness report
dbt source freshness

# Xem debug info
dbt debug

# Full refresh (rebuild models)
dbt run --full-refresh
```

### 5. Xem DBT Documentation

```bash
# Generate documentation
docker compose exec dbt dbt docs generate

# Serve documentation (trong browser)
docker compose exec dbt dbt docs serve

# Truy cập: http://localhost:8000
```

### 6. Reload Data

```bash
# Xóa dữ liệu và reload từ JSON
docker compose exec dbt python /workspace/main.py

# Rebuild dbt models
docker compose exec dbt dbt run --full-refresh
```

---

## Hướng Dẫn Sử Dụng DBT với Oracle Database

### 1. Thiết Lập Kết Nối Oracle

```bash
# Bước 1: Cài đặt dbt-oracle adapter
pip install dbt-oracle

# Bước 2: Cấu hình profiles.yml với Oracle connection
# Xem phần "Kết Nối Với Các Data Warehouse > DBT + Oracle Database"

ORACLE_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data_src"

def get_connection():
    # print("Connecting to PostgreSQL...", DB_CONFIG)
    return oracledb.connect(**ORACLE_CONFIG)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data_src"

def get_connection():
    # print("Connecting to PostgreSQL...", DB_CONFIG)
    return psycopg2.connect(**DB_CONFIG)


# Bước 3: Test kết nối
dbt debug

# Output mong đợi:
# Connection:
#   type: oracle
#   host: oracle.example.com
#   user: dbt_user
#   service_name: ORCL
#   state: Open
#
# ✓ Yêu cầu thành công: "state: Open"
# ✗ Sai: "state: Closed" hoặc "ORA-12514"
```

### 2. Truy Cập Oracle Database

#### Cách 1: Dùng SQL*Plus

```bash
# Kết nối tới Oracle
sqlplus dbt_user/your_password@ORCL

# Các lệnh SQL*Plus hữu ích:
desc dbt_dev.stg_users;              -- Chi tiết table structure
select * from dbt_dev.stg_users;     -- Xem dữ liệu
select count(*) from dbt_dev.fct_orders; -- Đếm rows
exit;                                -- Thoát
```

#### Cách 2: Kết nối với SQL Developer / IDE

```
Connection Type: Oracle
Host: oracle.example.com
Port: 1521
Service Name: ORCL
Username: dbt_user
Password: your_password

✓ Yêu cầu thành công: Kết nối thành công, xem được tables
```

### 3. Truy Vấn Dữ Liệu Trên Oracle

```sql
-- KIỂM TRA CẤU TRÚC BẢNG
desc dbt_dev.stg_users;
desc dbt_dev.fct_orders;

-- KIỂM TRA DỮ LIỆU STAGING
select * from dbt_dev.stg_users where rownum <= 3;
 
-- Kết quả:
-- USER_ID | USER_NAME   | EMAIL              
-- --------|-------------|--------------------
-- 10      | John Doe    | john@example.com   
-- 15      | Jane Smith  | jane@example.com   
-- 12      | Bob Wilson  | bob@example.com

-- KIỂM TRA DỮ LIỆU MART (FACT TABLE)
select 
    order_id, 
    user_id, 
    user_name, 
    email,
    total_amount,
    created_at
from dbt_dev.fct_orders 
where rownum <= 3;

-- THỐNG KÊ SỐ LƯỢNG
select count(*) as total_orders from dbt_dev.stg_orders;
-- Output: TOTAL_ORDERS = 150

select count(distinct user_id) as unique_users from dbt_dev.stg_users;
-- Output: UNIQUE_USERS = 50

-- AGGREGATION
select 
    user_id, 
    count(*) as order_count, 
    sum(total_amount) as total_spent
from dbt_dev.fct_orders
group by user_id
order by total_spent desc
fetch first 5 rows only;

-- KIỂM TRA TABLESPACE VÀ KÍCH THƯỚC
select segment_name, segment_type, bytes/1024/1024 as mb
from user_segments
where segment_name in ('STG_USERS', 'STG_ORDERS', 'FCT_ORDERS');
```

### 4. Chạy DBT Pipeline Trên Oracle

```bash
# Parse project
dbt parse

# Output:
# Running with dbt=1.5.0
# Found 3 models, 5 tests

# Chạy models
dbt run

# Output mong đợi:
# Running 1 of 3 START table model dbt_demo.stg_users
# Running 1 of 3 PASS table model dbt_demo.stg_users [CREATE TABLE 1.23s]
#
# Running 2 of 3 START table model dbt_demo.stg_orders
# Running 2 of 3 PASS table model dbt_demo.stg_orders [CREATE TABLE 1.15s]
#
# Running 3 of 3 START table model dbt_demo.fct_orders
# Running 3 of 3 PASS table model dbt_demo.fct_orders [CREATE TABLE 1.45s]
#
# Finished running 3 models in 3.83s.

# ✓ Yêu cầu thành công: Tất cả models = PASS

# Chạy tests
dbt test

# Output mong đợi:
# Running test not_null_stg_users_user_id ... PASS [0.15s]
# Running test unique_stg_users_user_id ... PASS [0.14s]
# Running test order_amount_positive ... PASS [0.12s]
#
# Finished running 5 tests in 0.78s.

# ✓ Yêu cầu thành công: Tất cả tests = PASS
```

### 5. Khắc Phục Sự Cố Oracle

**Lỗi: ORA-12514: TNS:listener does not currently know of service**

```sql
-- Kiểm tra service name
select name from v$database;

-- Kiểm tra listener status
-- Chạy: lsnrctl status (từ command line OS)
```

**Lỗi: ORA-01031: insufficient privileges**

```sql
-- Grant cần thiết cho dbt user
grant create session to dbt_user;
grant create table to dbt_user;
grant create view to dbt_user;
grant unlimited tablespace to dbt_user;
```

---

## Hướng Dẫn Sử Dụng DBT với Redshift

### 1. Thiết Lập Kết Nối Redshift

```bash
# Bước 1: Cài đặt dbt-redshift adapter
pip install dbt-redshift

# Bước 2: Cấu hình profiles.yml với Redshift connection
# Xem phần "Kết Nối Với Các Data Warehouse > DBT + Amazon Redshift"

DB_CONFIG = {
    "host": os.getenv("REDSHIFT_HOST"),
    "port": os.getenv("REDSHIFT_PORT"),
    "dbname": os.getenv("REDSHIFT_DB"),
    "user": os.getenv("REDSHIFT_USER"),
    "password": os.getenv("REDSHIFT_PASSWORD"),
}

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data_src"

def get_connection():
    # print("Connecting to REDSHIFT...", DB_CONFIG)
    return psycopg2.connect(**DB_CONFIG)


# Bước 3: Test kết nối
dbt debug

# Output mong đợi:
# Connection:
#   type: redshift
#   host: redshift-cluster.abc123.us-east-1.redshift.amazonaws.com
#   user: admin
#   dbname: analytics
#   state: Open
#
# ✓ Yêu cầu thành công: "state: Open"
# ✗ Sai: "state: Closed" hoặc "Connection refused"
```

### 2. Truy Cập Redshift Database

#### Cách 1: Dùng psql CLI

```bash
# Cài đặt PostgreSQL client tools (nếu chưa có)
# Windows: Download từ PostgreSQL installer
# MacOS: brew install postgresql
# Linux: apt-get install postgresql-client

# Kết nối tới Redshift
psql -h redshift-cluster.abc123.us-east-1.redshift.amazonaws.com \
     -U admin \
     -d analytics \
     -p 5439

# Các lệnh psql hữu ích:
\dn                           -- List schemas
\dt                           -- List tables
\dt dbt_dev.*                 -- List tables trong dbt_dev
\d dbt_dev.stg_users         -- Chi tiết columns
\q                           -- Thoát
```

#### Cách 2: Kết nối với IDE (Dbeaver, SQL Workbench)

```
Connection Type: Redshift (hoặc PostgreSQL)
Host: redshift-cluster.abc123.us-east-1.redshift.amazonaws.com
Port: 5439
Username: admin
Password: your_password
Database: analytics

✓ Yêu cầu thành công: Kết nối thành công, xem được tables
```

### 3. Truy Vấn Dữ Liệu Trên Redshift

```sql
-- KIỂM TRA DỮ LIỆU STAGING
select * from dbt_dev.stg_users limit 3;

-- Kết quả:
-- user_id | user_name   | email              
-- --------|-------------|--------------------
-- 10      | John Doe    | john@example.com   
-- 15      | Jane Smith  | jane@example.com   

-- KIỂM TRA DỮ LIỆU MART
select 
    order_id, 
    user_id, 
    user_name,
    total_amount,
    created_at
from dbt_dev.fct_orders
limit 5;

-- THỐNG KÊ
select count(*) as total_orders from dbt_dev.stg_orders;
-- Output: 150

select count(distinct user_id) as unique_users from dbt_dev.stg_users;
-- Output: 50

-- AGGREGATION VÀ SORTING
select 
    user_id,
    count(*) as order_count,
    sum(total_amount) as total_spent
from dbt_dev.fct_orders
group by user_id
order by total_spent desc
limit 5;

-- REDSHIFT-SPECIFIC: Xem dung lượng bảng
select schemaname, tablename, size
from svv_table_info
where schemaname = 'dbt_dev'
order by size desc;

-- REDSHIFT-SPECIFIC: Performance monitoring
select query, starttime, duration, status
from stl_query
where userid > 1
order by starttime desc
limit 10;
```

### 4. Chạy DBT Pipeline Trên Redshift

```bash
# Parse project
dbt parse

# Chạy models
dbt run

# Output mong đợi (Redshift chậm hơn PostgreSQL):
# Running 1 of 3 START table model dbt_demo.stg_users
# Running 1 of 3 PASS table model dbt_demo.stg_users [CREATE TABLE 5.23s]
#
# Running 2 of 3 START table model dbt_demo.stg_orders
# Running 2 of 3 PASS table model dbt_demo.stg_orders [CREATE TABLE 4.87s]
#
# Running 3 of 3 START table model dbt_demo.fct_orders
# Running 3 of 3 PASS table model dbt_demo.fct_orders [CREATE TABLE 6.12s]
#
# Finished running 3 models in 16.22s.

# Lưu ý: Redshift thường chậm hơn do compile trên MPP architecture

# Chạy tests
dbt test

# Output:
# Running 5 tests in parallel
# Running test not_null_stg_users_user_id ... PASS [0.45s]
# Running test unique_stg_users_user_id ... PASS [0.38s]
# Running test order_amount_positive ... PASS [0.42s]
#
# Finished running 5 tests in 0.82s.
```

### 5. Tối Ưu Hóa Cho Redshift

```bash
# Chạy với incremental models (nếu có)
dbt run --models +fct_orders  # Chỉ chạy fct_orders và dependencies

# Full refresh (rebuild toàn bộ)
dbt run --full-refresh

# Chạy với debug mode
dbt run --debug
```

### 6. Khắc Phục Sự Cố Redshift

**Lỗi: Could not connect to server**

```bash
# Kiểm tra security group
# AWS Management Console > Redshift > Cluster > Security groups
# Đảm bảo inbound rules cho port 5439 được mở

# Kiểm tra credentials
dbt debug

# Kiểm tra cluster status
# AWS Management Console > Redshift > Clusters
```

**Lỗi: Query timed out**

```bash
# Redshift query quá lâu, có thể model quá lớn
# Giải pháp:
# 1. Sử dụng incremental materialization
# 2. Thêm distribution keys
# 3. Optimize queries
```

---

## Hướng Dẫn Sử Dụng DBT với Trino

### 1. Thiết Lập Kết Nối Trino

```bash
# Bước 1: Cài đặt dbt-trino adapter
pip install dbt-trino

# Bước 2: Cấu hình profiles.yml
# Xem phần "Kết Nối Với Các Data Warehouse > DBT + Trino"

TRINO_CONFIG = {
    "host": os.getenv("TRINO_HOST"),
    "port": int(os.getenv("TRINO_PORT", 8080)),
    "user": os.getenv("TRINO_USER"),
    "catalog": os.getenv("TRINO_CATALOG"),
    "schema": os.getenv("TRINO_SCHEMA")
}

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data_src"

def get_connection():
    # print("Connecting to Trino...", TRINO_CONFIG)
    return trino.dbapi.connect(**TRINO_CONFIG)


# Bước 3: Test kết nối
dbt debug

# Output mong đợi:
# Connection:
#   type: trino
#   host: trino-coordinator.example.com
#   port: 8080
#   user: dbt_user
#   database: hive
#   schema: dbt_dev
#   state: Open
#
# ✓ Yêu cầu thành công: "state: Open"
# ✗ Sai: "Connection refused", "Authentication failed"
```

### 2. Truy Cập Trino Database

#### Cách 1: Dùng trino-cli (Command Line)

```bash
# Cài đặt Trino CLI
# Download từ: https://repo1.maven.org/maven2/io/trino/trino-cli/

# Kết nối tới Trino
java -jar trino-cli-<version>-executable.jar \
  --server https://trino-coordinator.example.com:8080 \
  --user dbt_user \
  --catalog hive \
  --schema dbt_dev

# Các lệnh Trino SQL hữu ích:
show schemas;                    -- List schemas
show tables;                     -- List tables
desc dbt_dev.stg_users;         -- Chi tiết table
select * from dbt_dev.stg_users; -- Xem dữ liệu
exit;                           -- Thoát
```

#### Cách 2: Kết nối với Web UI

```
Trino có Web UI cho query monitoring:
- URL: http://trino-coordinator.example.com:8080
- Xem query execution plan
- Xem performance metrics
- Monitor running queries
```

#### Cách 3: Kết nối với IDE (DBeaver)

```
Connection Type: Trino
Host: trino-coordinator.example.com
Port: 8080
Catalog: hive (hoặc iceberg, postgres, etc.)
Schema: dbt_dev
Username: dbt_user
Password: your_password

✓ Yêu cầu thành công: Kết nối thành công, xem được tables
```

### 3. Truy Vấn Dữ Liệu Trên Trino

```sql
-- KIỂM TRA CẤU TRÚC
describe hive.dbt_dev.stg_users;

-- KIỂM TRA DỮ LIỆU STAGING
select * from hive.dbt_dev.stg_users limit 3;

-- Kết quả:
-- user_id | user_name   | email              
-- --------|-------------|--------------------
-- 10      | John Doe    | john@example.com   
-- 15      | Jane Smith  | jane@example.com   

-- KIỂM TRA DỮ LIỆU MART
select 
    order_id, 
    user_id, 
    user_name,
    email,
    total_amount,
    created_at
from hive.dbt_dev.fct_orders
limit 5;

-- THỐNG KÊ
select count(*) as total_orders from hive.dbt_dev.stg_orders;
-- Output: 150

select count(distinct user_id) as unique_users from hive.dbt_dev.stg_users;
-- Output: 50

-- AGGREGATION
select 
    user_id,
    count(*) as order_count,
    sum(total_amount) as total_spent
from hive.dbt_dev.fct_orders
group by user_id
order by total_spent desc
limit 5;

-- TRINO-SPECIFIC: Xem metadata
select * from system.metadata.table_comments
where table_schema = 'dbt_dev';

-- TRINO-SPECIFIC: Xem columns
select table_name, column_name, data_type
from information_schema.columns
where table_schema = 'dbt_dev'
order by table_name, ordinal_position;

-- TRINO-SPECIFIC: Query history (từ Web UI)
-- Vào http://trino-coordinator.example.com:8080
-- Xem Failed, Queued, Running, Finished queries
```

### 4. Chạy DBT Pipeline Trên Trino

```bash
# Parse project
dbt parse

# Chạy models
dbt run

# Output mong đợi:
# Running 1 of 3 START table model dbt_demo.stg_users
# Running 1 of 3 PASS table model dbt_demo.stg_users [CREATE TABLE USING ICEBERG 8.45s]
#
# Running 2 of 3 START table model dbt_demo.stg_orders
# Running 2 of 3 PASS table model dbt_demo.stg_orders [CREATE TABLE USING ICEBERG 7.23s]
#
# Running 3 of 3 START table model dbt_demo.fct_orders
# Running 3 of 3 PASS table model dbt_demo.fct_orders [CREATE TABLE USING ICEBERG 6.12s]
#
# Finished running 3 models in 22.1s.

# Lưu ý: Trino tạo ICEBERG tables (nếu backend là Iceberg)

# Chạy tests
dbt test

# Output:
# Running test not_null_stg_users_user_id ... PASS [0.55s]
# Running test unique_stg_users_user_id ... PASS [0.48s]
# Running test order_amount_positive ... PASS [0.52s]
#
# Finished running 5 tests in 1.15s.
```

### 5. Trino-Specific Features

```bash
# Chạy trên catalog khác (nếu cấu hình Iceberg)
# Thay đổi profiles.yml:
# database: iceberg # Thay vì hive

# Chạy với parallel execution
dbt run --threads 8

# Chạy incremental model
dbt run --models +fct_orders_incremental

# Xem compiled SQL
cat target/compiled/dbt_demo/models/marts/fct_orders.sql
```

### 6. Khắc Phục Sự Cố Trino

**Lỗi: Catalog not found**

```bash
# Kiểm tra catalogs có sẵn
# Từ Trino CLI: show catalogs;
# Hoặc từ Web UI: Catalogs tab

# Kiểm tra profiles.yml
# Đảm bảo `database:` chỉ tới catalog tồn tại
```

**Lỗi: User not authorized**

```bash
# Kiểm tra Trino authentication
# Có thể cần cấu hình:
# - LDAP
# - OAuth2
# - Kerberos

# Trong profiles.yml, thêm authentication:
# ssl: true
# ca_path: /path/to/ca.pem
```

**Lỗi: Schema not found**

```bash
# Kiểm tra schema tồn tại
# Từ Trino CLI: show schemas in hive;
# Hoặc tạo schema mới:
# create schema hive.dbt_dev;
```

---

## Docker Configuration

### docker-compose.yml
Định nghĩa 2 services:

#### PostgreSQL Service
```yaml
services:
  postgres:
    image: postgres:15                    # PostgeSQL 15
    container_name: postgres-dbt
    environment:
      POSTGRES_USER: postgres             # Default user
      POSTGRES_PASSWORD: postgres         # Default password
      POSTGRES_DB: analytics              # Default database
    ports:
      - "5432:5432"                       # Map port
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persist data
```

#### DBT Service
```yaml
  dbt:
    build:
      context: .
      dockerfile: Dockerfile              # Build từ Dockerfile
    container_name: dbt-postgres
    depends_on:
      - postgres                          # Chuyên chờ postgres ready
    volumes:
      - .:/workspace                      # Mount project folder
      - ./profiles.yml:/root/.dbt/profiles.yml  # DBT config
    working_dir: /workspace/dbt_demo      # Working directory
    environment:
      DBT_PROFILES_DIR: /root/.dbt        # DBT profiles location
    entrypoint: ["tail", "-f", "/dev/null"]  # Keep running
```

### Dockerfile
```dockerfile
FROM python:3.10-slim                     # Base image

RUN pip install --no-cache-dir \
    dbt-postgres \                        # dbt adapter cho PostgreSQL
    psycopg2-binary                       # PostgreSQL 
    client
    python-dotenv

WORKDIR /usr/app                          # Working directory
```

---

## Configuration Files

### profiles.yml
Cấu hình kết nối DBT đến database:

```yaml
dbt_demo:               # Target name (dbt_project.yml reference)
  target: dev          # Active target
  
  outputs:
    dev:
      type: postgres              # Database type
      host: postgres              # Service name (docker)
      user: postgres              # User
      password: postgres          # Password
      port: 5432                  # Port
      dbname: analytics           # Database
      schema: dbt_dev             # Schema for models
      threads: 4                  # Parallel execution threads
```

### dbt_project.yml
Cấu hình DBT project:

```yaml
name: "dbt_demo"                  # Project name
version: "1.0"                    # Version
config-version: 2                 # Config version

profile: "dbt_demo"              # Profile name

model-paths: ["models"]           # Models directory

models:
  dbt_demo:
    staging:
      +materialized: view         # staging models = VIEWs
    marts:
      +materialized: table        # mart models = TABLEs
```

---

## Workflow Tiêu Biểu

### Day 1: Setup Mới

```bash
# 1. Clone / Copy project
cd \Demo\demo_dbt

# 2. Start services
docker compose up -d --build

# 3. Load dữ liệu
docker compose exec dbt python /workspace/main.py

# 4. Build models + tests
docker compose exec dbt dbt build

# 5. Kiểm tra kết quả
docker compose exec -it postgres-dbt psql -U postgres -d analytics
> select * from dbt_dev.fct_orders;
```

### Daily: Development

```bash
# 1. Xem logs
docker compose logs -f

# 2. Modify models (stg_*.sql hoặc fct_*.sql)

# 3. Rerun models
docker compose exec dbt dbt run

# 4. Check tests
docker compose exec dbt dbt test

# 5. Truy vấn kết quả
docker exec -it postgres-dbt psql -U postgres -d analytics
```

### Maintenance: Cleanup

```bash
# Stop services
docker compose down

# Remove volumes (delete data)
docker compose down -v

# Rebuild từ đầu
docker compose up -d --build
```

---

## Troubleshooting

### 1. Cannot Connect to PostgreSQL

**Vấn đề:** Connection refused on 5432

**Giải pháp:**
```bash
# Check service running
docker compose ps

# Restart services
docker compose restart postgres

# Check logs
docker compose logs postgres
```

### 2. DBT Models Failed

**Vấn đề:** dbt run error

**Giải pháp:**
```bash
# Check syntax
docker compose exec dbt dbt parse

# Debug mode
docker compose exec dbt dbt run --debug

# Full logs
cat dbt_demo/logs/dbt.log
```

### 3. Data Load Failed

**Vấn đề:** main.py error

**Giải pháp:**
```bash
# Check data files exist
ls -la Data_src/

# Check JSON format
python -m json.tool Data_src/orders.json

# Run with verbose
docker compose exec dbt python -u /workspace/main.py
```

### 4. Tests Failed

**Vấn đề:** dbt test errors

**Giải pháp:**
```bash
# Run tests verbose
docker compose exec dbt dbt test --debug

# Run specific test
docker compose exec dbt dbt test -s stg_orders

# View test results
cat dbt_demo/target/run_results.json
```

### 5. Port Already in Use

**Vấn đề:** Port 5432 đã được sử dụng

**Giải pháp:**
```bash
# Kill process using port
netstat -ano | findstr :5432
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
# ports:
#   - "5433:5432"
```

### 6. Permission Denied

**Vấn đề:** Permission error khi mount volumes

**Giải pháp:**
```bash
# Run Docker as Administrator
# Or adjust file permissions
chmod -R 777 .
```

---

## Performance Tuning

### 1. Parallel Processing
Tăng threads trong profiles.yml:
```yaml
threads: 8  # From 4 to 8
```

### 2. Incremental Models
Cho models lớn, sử dụng incremental materialization:
```sql
{{ config(
    materialized='incremental'
) }}

select ... 
from raw.orders_raw
{% if execute %}
  where created_at > (select max(created_at) from {{ this }})
{% endif %}
```

### 3. Database Indexing
Thêm indexes trên frequently queried columns:
```sql
create index idx_orders_user_id on dbt_dev.fct_orders(user_id);
create index idx_orders_created_at on dbt_dev.fct_orders(created_at);
```

---

## Best Practices

### 1. Model Organization
- Clarity trong naming: `stg_source_concept`, `fct_concept`
- Separation of concerns: Raw → Staging → Marts
- One model per file

### 2. Testing Strategy
- Test primary keys: `unique`, `not_null`
- Test relationships: Foreign key constraints
- Test business logic: Custom tests
- Min 80% model column coverage

### 3. Documentation
- Thêm descriptions trong schema.yml
- Sử dụng dbt docs
- Comment trên complex logic

### 4. Version Control
- Commit models và tests
- Exclude: logs/, target/, dbt_packages/
- Use meaningful commits: "Add user demographics to fct_orders"

### 5. Deployment
- Test locally trước
- Use dbt artifacts (manifest.json)
- Schedule regular builds
- Monitor data quality

---

## Resource Links

### Official Documentation
- [DBT Documentation](https://docs.getdbt.com)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

### Learning Resources
- [DBT Tutorial](https://docs.getdbt.com/tutorial/getting-set-up/overview)
- [SQL Best Practices](https://mode.com/sql-tutorial/)
- [Data Modeling](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/

---

## Support & Maintainer

**Project:** DBT Demo - Data Pipeline
**Created:** 2026-03-12
**Version:** 1.0

### Quick Support
1. Kiểm tra logs: `docker compose logs`
2. Debug mode: `dbt run --debug`
3. Check database: `psql` console
4. Rebuild: `docker compose up -d --build`

---

## Appendix: SQL Cheat Sheet

```sql
-- Databases
create database analytics;
drop database analytics;

-- Schemas
create schema raw;
create schema dbt_dev;

-- Tables
\d raw.orders_raw          -- Describe table
select * from raw.orders_raw;

-- Data Statistics
select count(*) as cnt from raw.orders_raw;
select count(distinct user_id) from raw.orders_raw;

-- Joins
select 
    o.order_id,
    o.user_id,
    u.user_name
from raw.orders_raw o
left join raw.users_raw u
    on o.user_id = u.user_id;

-- Aggregations
select 
    user_id,
    count(*) as order_count,
    sum(total_amount) as total_spent
from raw.orders_raw
group by user_id
order by total_spent desc;

-- Date Functions
select 
    date_trunc('month', created_at) as order_month,
    count(*) as order_count
from raw.orders_raw
group by date_trunc('month', created_at);
```

---

**Last Updated:** 2026-03-12  
**Status:** Active  
**Maintainer:** Data Team
