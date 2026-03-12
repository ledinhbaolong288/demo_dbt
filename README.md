# DBT Demo Project - Tài liệu Demo DBT với Posgres trên Docker

## Mục Lục
1. [Tổng Quan](#tổng-quan)
2. [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
3. [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
4. [Cài Đặt và Khởi Động](#cài-đặt-và-khởi-động)
5. [Cấu Trúc Dữ Liệu](#cấu-trúc-dữ-liệu)
6. [Pipeline ETL](#pipeline-etl)
7. [Các Mô Hình DBT](#các-mô-hình-dbt)
8. [Data Quality Tests](#data-quality-tests)
9. [Hướng Dẫn Sử Dụng](#hướng-dẫn-sử-dụng)
10. [Khắc Phục Sự Cố](#khắc-phục-sự-cố)

---

## Tổng Quan

**DBT Demo Project** là một dự án mẫu xây dựng ETL pipeline với các công cụ:
- **DBT (Data Build Tool)**: Quản lý các transformation SQL
- **PostgreSQL**: Cơ sở dữ liệu lưu trữ
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
- **5432**: PostgreSQL database (localhost:5432)

---

## Cài Đặt và Khởi Động

### 1. Chuẩn Bị Môi Trường

```bash
# Copy file hiện tại về thư mục làm việc
cd \Demo\demo_dbt

# Chuẩn bị các package install trên file Dockerfile
- dbt-postgres # Thư viện dbt trên db postgres
- psycopg2-binary # Thư viện kết nối với postgres
- python-dotenv # Thư viện đọc env

# Kiểm tra Docker đang chạy
docker --version
docker compose --version
```

### 2. Khởi Động Services

```bash
# Build image và khởi động services
docker compose up -d --build

# Xác nhận services đã chạy
docker compose ps
```

Output mong đợi:
```
CONTAINER ID   IMAGE              STATUS
...            postgres:15        Up ...
...            dbt-postgres       Up ...
```

### 3. Load Dữ Liệu Ban Đầu

```bash
# Chạy Python script để tạo bảng raw và load dữ liệu
docker compose exec dbt python /workspace/main.py

# Output:
# Raw tables created and data loaded successfully!
```

### 4. Chạy DBT Pipeline

```bash
# Thực hiện toàn bộ pipeline (build models + run tests)
docker compose exec dbt dbt build

# Hoặc chạy riêng từng phần:
docker compose exec dbt dbt run           # Chỉ build models
docker compose exec dbt dbt test          # Chỉ chạy tests
docker compose exec dbt dbt snapshot      # Tạo snapshots
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
       "host": "postgres",
       "port": 5432,
       "dbname": "analytics",
       "user": "postgres",
       "password": "postgres",
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

Lớp staging làm sạch và chuẩn hóa dữ liệu từ raw tables.

#### stg_orders.sql
```sql
select
    cast(order_id as bigint) as order_id,
    cast(user_id as bigint) as user_id,
    cast(total_amount as numeric(18,2)) as total_amount,
    cast(created_at as timestamp) as created_at,
    cast(etl_time as timestamp) as etl_time
from raw.orders_raw
```

**Mục đích:**
- Cast đúng kiểu dữ liệu
- Loại bỏ các cột không cần thiết
- Chuẩn hóa naming convention

**Materialization:** VIEW (được cấu hình trong dbt_project.yml)

#### stg_users.sql
```sql
select
    cast(user_id as bigint) as user_id,
    trim(user_name) as user_name,
    lower(trim(email)) as email,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at,
    cast(etl_time as timestamp) as etl_time
from raw.users_raw
```

**Đặc điểm:**
- Trim whitespace từ text fields
- Normalize email thành lowercase
- Cast timestamps

**Materialization:** VIEW

### 2. Mart Models (dbt_dev.fct_*)

Lớp mart chứa business logic tổng hợp, sẵn sàng cho analytics.

#### fct_orders.sql
```sql
select
    o.order_id,
    o.user_id,
    u.user_name,
    u.email,
    o.total_amount,
    o.created_at
from {{ ref('stg_orders') }} o
left join {{ ref('stg_users') }} u
    on o.user_id = u.user_id
```

**Đặc điểm:**
- Join orders + users thông tin
- Chứa đầy đủ context cho analysis
- Sử dụng Jinja macros `{{ ref() }}` để tham chiếu models

**Materialization:** TABLE (được cấu hình trong dbt_project.yml)

---

## Data Quality Tests

DBT tích hợp data quality validations thông qua `schema.yml`.

### Configuration (schema.yml)

```yaml
version: 2

models:
  - name: stg_orders
    columns:
      - name: order_id
        tests:
          - not_null    # order_id không được NULL
          - unique      # order_id phải unique
      
      - name: user_id
        tests:
          - not_null
          - relationships:  # Constraint FK
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

### Built-in Tests

| Test | Mô Tả | Ví Dụ |
|------|-------|-------|
| `not_null` | Kiểm tra null values | `not_null` kiểm tra NULL records |
| `unique` | Kiểm tra duplicate values | `unique` kiểm tra duplicate IDs |
| `relationships` | Kiểm tra foreign key constraint | Validate order_id tồn tại trong stg_orders |
| `accepted_values` | Kiểm tra giá trị nằm trong list | `accepted_values: [1,2,3]` |

### Custom Tests (order_amount_positive.sql)

```sql
select *
from {{ ref('fct_orders') }}
where total_amount <= 0
```

**Mục đích:** Kiểm tra tất cả order amounts phải > 0

**Cách hoạt động:**
- Nếu query trả về 0 rows → Test PASS ✓
- Nếu query trả về records → Test FAIL ✗

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
