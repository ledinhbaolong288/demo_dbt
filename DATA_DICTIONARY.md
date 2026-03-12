# Data Dictionary - DBT Demo Project

Complete reference for all tables, columns, and their definitions.

## Table of Contents
1. [Raw Layer](#raw-layer)
2. [Staging Layer](#staging-layer)
3. [Mart Layer](#mart-layer)
4. [Data Lineage](#data-lineage)
5. [Business Metrics](#business-metrics)

---

## Raw Layer

Raw layer contains unprocessed data directly from source systems.

### raw.orders_raw

Source data table for all orders from JSON import.

| Column Name | Data Type | Nullable | Description |
|---|---|---|---|
| order_id | bigint | NO | Unique identifier for each order. Primary Key. |
| user_id | bigint | NO | Identifier of the user who placed the order. References raw.users_raw. Foreign Key. |
| total_amount | numeric(18,2) | NO | Total monetary value of the order. Always ≥ 0. |
| created_at | timestamp | NO | Timestamp when the order was created. |
| etl_time | timestamp | NO (default CURRENT_TIMESTAMP) | Timestamp when the record was loaded into the warehouse. Used to track data freshness. |

**Row Count:** Varies (depends on JSON file)
**Update Frequency:** On-demand (manual load via main.py)
**Business Owner:** Data Engineering Team
**Data Quality:** Raw, unvalidated

### raw.users_raw

Source data table for all user profiles from JSON import.

| Column Name | Data Type | Nullable | Description |
|---|---|---|---|
| user_id | bigint | NO | Unique identifier for each user. Primary Key. |
| user_name | text | NO | Full name of the user. May contain leading/trailing whitespace. |
| email | text | NO | Email address of the user. Mixed case in source. |
| created_at | timestamp | NO | Timestamp when the user account was created. |
| updated_at | timestamp | NO | Timestamp of the last update to the user profile. |
| etl_time | timestamp | NO (default CURRENT_TIMESTAMP) | Timestamp when the record was loaded into the warehouse. |

**Row Count:** Varies (depends on JSON file)
**Update Frequency:** On-demand (manual load via main.py)
**Business Owner:** Data Engineering Team
**Data Quality:** Raw, unvalidated

---

## Staging Layer

Staging layer contains cleaned and standardized data. All data types are verified and normalized.

### dbt_dev.stg_orders

Cleaned staging table for orders.

| Column Name | Data Type | Source Column | Transformations | Nullable | Tests |
|---|---|---|---|---|---|
| order_id | bigint | raw.orders_raw.order_id | Type cast to bigint | NO | unique, not_null |
| user_id | bigint | raw.orders_raw.user_id | Type cast to bigint | NO | not_null, relationships → stg_users |
| total_amount | numeric(18,2) | raw.orders_raw.total_amount | Type cast to numeric | NO | not_null |
| created_at | timestamp | raw.orders_raw.created_at | Type cast to timestamp | NO | not_null |
| etl_time | timestamp | raw.orders_raw.etl_time | Type cast to timestamp | NO | not_null |

**Materialization:** VIEW
**Row Count:** Same as raw.orders_raw
**Refresh Frequency:** Real-time (VIEW)
**Purpose:** Data type validation and column selection
**Data Quality:** Validated (all columns not_null)

**Sample Query:**
```sql
select * from dbt_dev.stg_orders limit 5;
```

### dbt_dev.stg_users

Cleaned staging table for users.

| Column Name | Data Type | Source Column | Transformations | Nullable | Tests |
|---|---|---|---|---|---|
| user_id | bigint | raw.users_raw.user_id | Type cast to bigint | NO | unique, not_null |
| user_name | text | raw.users_raw.user_name | Trim whitespace, type cast | NO | not_null, unique |
| email | text | raw.users_raw.email | Lowercase, trim whitespace, type cast | NO | not_null, unique |
| created_at | timestamp | raw.users_raw.created_at | Type cast to timestamp | NO | not_null |
| updated_at | timestamp | raw.users_raw.updated_at | Type cast to timestamp | NO | not_null |
| etl_time | timestamp | raw.users_raw.etl_time | Type cast to timestamp | NO | not_null |

**Materialization:** VIEW
**Row Count:** Same as raw.users_raw
**Refresh Frequency:** Real-time (VIEW)
**Purpose:** 
  - Text standardization (trim, lowercase)
  - Data type validation
  - Ensure uniqueness of key attributes

**Data Quality:** 
  - All columns not_null ✓
  - user_id, user_name, email are unique ✓
  - Appropriate data types ✓

**Sample Query:**
```sql
select * from dbt_dev.stg_users limit 5;
```

---

## Mart Layer

Mart layer contains business-ready analytics data.

### dbt_dev.fct_orders

Fact table for orders with enriched customer information.

| Column Name | Data Type | Source Table | Description | Null Handling | Business Meaning |
|---|---|---|---|---|---|
| order_id | bigint | stg_orders | Unique order identifier | NOT NULL (PK) | Core order transaction identifier |
| user_id | bigint | stg_orders | User who placed order | NOT NULL (FK) | Customer identifier for grouping |
| user_name | text | stg_users | Customer full name (via join) | NOT NULL | Used in user-facing reports |
| email | text | stg_users | Customer email (via join) | NOT NULL | Used for customer contact lists |
| total_amount | numeric(18,2) | stg_orders | Order total value in dollars | NOT NULL | Used for revenue analysis |
| created_at | timestamp | stg_orders | Order creation timestamp | NOT NULL | Used for time-based analysis |

**Materialization:** TABLE
**Row Count:** Same as stg_orders
**Refresh Frequency:** Full rebuild (manual trigger)
**Primary Key:** order_id
**Foreign Keys:** 
  - user_id → stg_users(user_id)
  - order_id → stg_orders(order_id)

**Join Logic:**
```sql
stg_orders (o)
  LEFT JOIN stg_users (u) 
    ON o.user_id = u.user_id
```

**Data Quality Tests:**
- order_id: unique, not_null ✓
- user_id: not_null, relationships → stg_users(user_id) ✓
- total_amount: not_null, > 0 (custom test) ✓

**Sample Queries:**

Total orders by user:
```sql
select 
    user_name,
    count(*) as order_count,
    sum(total_amount) as total_revenue
from dbt_dev.fct_orders
group by user_name
order by total_revenue desc;
```

Recent orders:
```sql
select 
    order_id,
    user_name,
    email,
    total_amount,
    created_at
from dbt_dev.fct_orders
where created_at >= current_date - interval '30 days'
order by created_at desc;
```

---

## Data Lineage

### Lineage Diagram

```
Data Sources (JSON)
├── orders.json
│   └── Parser (main.py)
│       └── raw.orders_raw
│           └── (dbt) stg_orders (VIEW)
│               └── (dbt) fct_orders (TABLE)
│
└── users.json
    └── Parser (main.py)
        └── raw.users_raw
            └── (dbt) stg_users (VIEW)
                └── (dbt) fct_orders (TABLE) [via JOIN]
```

### Dependency Chain

```sql
fct_orders depends on:
├── stg_orders (direct)
│   └── raw.orders_raw (source)
│       └── Data_src/orders.json (file)
│
└── stg_users (via JOIN)
    └── raw.users_raw (source)
        └── Data_src/users.json (file)
```

---

## Business Metrics

### Derived Metrics (Examples)

These metrics can be calculated from the mart tables:

#### Order Metrics

| Metric | Formula | SQL Example |
|--------|---------|---|
| Total Orders | COUNT(*) | `select count(*) from fct_orders;` |
| Total Revenue | SUM(total_amount) | `select sum(total_amount) from fct_orders;` |
| Average Order Value | SUM(total_amount) / COUNT(*) | `select avg(total_amount) from fct_orders;` |
| Max Order Value | MAX(total_amount) | `select max(total_amount) from fct_orders;` |
| Min Order Value | MIN(total_amount) | `select min(total_amount) from fct_orders;` |

#### Customer Metrics

| Metric | Formula | SQL Example |
|--------|---------|---|
| Total Customers | COUNT(DISTINCT user_id) | `select count(distinct user_id) from fct_orders;` |
| Orders per Customer | COUNT(*) / COUNT(DISTINCT user_id) | `select count(*) / count(distinct user_id) as avg_orders from fct_orders;` |
| Customer LTV | SUM(total_amount) per user_id | `select user_id, sum(total_amount) as customer_lifetime_value from fct_orders group by user_id;` |

#### Time-Based Metrics

| Metric | SQL |
|--------|-----|
| Daily Revenue | `select date(created_at) as date, sum(total_amount) as daily_revenue from fct_orders group by date(created_at);` |
| Monthly Revenue | `select date_trunc('month', created_at)::date as month, sum(total_amount) as monthly_revenue from fct_orders group by date_trunc('month', created_at);` |
| Year-to-Date Revenue | `select sum(total_amount) from fct_orders where year(created_at) = year(current_date);` |

---

## Data Types Reference

### PostgreSQL Data Types Used

| Data Type | Bytes | Description | Example |
|-----------|-------|---|---|
| bigint | 8 | 64-bit integer | 9223372036854775807 |
| text | Variable | String of any length | 'John Doe' |
| numeric(18,2) | Variable | Fixed-point decimal | 9999999999999999.99 |
| timestamp | 8 | Date and time | 2024-03-12 14:30:00 |

---

## ETL Statistics

### Data Load Volume

```
JSON Source Files:
├── orders.json: [size]
└── users.json: [size]

Raw Tables (after load):
├── raw.orders_raw: [row_count] rows
└── raw.users_raw: [row_count] rows

Staging Views (virtual):
├── stg_orders: [row_count] rows (VIEW - no storage)
└── stg_users: [row_count] rows (VIEW - no storage)

Mart Tables:
└── fct_orders: [row_count] rows ([storage_size])
```

### Data Quality Summary

```
Raw Tables:
  orders_raw:
    ├── Nulls allowed: YES
    ├── Duplicates allowed: YES
    └── Data quality score: ⚠️ Low (Raw data)
  
  users_raw:
    ├── Nulls allowed: YES
    ├── Duplicates allowed: YES
    └── Data quality score: ⚠️ Low (Raw data)

Staging Tables:
  stg_orders:
    ├── Nulls allowed: NO
    ├── Duplicates allowed: YES (on non-ID fields)
    └── Data quality score: ✓ High (Validated)
  
  stg_users:
    ├── Nulls allowed: NO
    ├── Duplicates allowed: NO (on ID, email, username)
    └── Data quality score: ✓ High (Validated)

Mart Tables:
  fct_orders:
    ├── Nulls allowed: NO
    ├── Duplicates: NO (on order_id)
    └── Data quality score: ✓ Excellent (Fully tested)
```

---

## Access & Permissions

### Database Access

| Role | Schema Access | Permission | Use Case |
|------|---|---|---|
| Analytics Users | dbt_dev (mats only) | SELECT | Query reports |
| Data Analysts | raw + dbt_dev | SELECT | Debug & analysis |
| Data Engineers | All | SELECT + DML | Development |
| DBT Service Account | All | SELECT + DML + DDL | ETL pipeline |

---

## Data Retention & Archival

### Data Retention Policy

```
Raw Tables:
  Retention: 1 year
  Archival: Compress & move to cold storage
  Deletion: After 2 years

Staging Tables:
  Retention: 3 years (VIEW - no storage)
  Archival: N/A (virtual tables)

Mart Tables:
  Retention: 3-5 years
  Archival: Compress after 3 years
  Deletion: After 5 years
```

---

## Glossary

| Term | Definition |
|------|-----------|
| **ETL** | Extract, Transform, Load |
| **ELT** | Extract, Load, Transform (DBT approach) |
| **Grain** | Atomic level of data (e.g., one row per order) |
| **Fact Table** | Table containing measurements/metrics (fct_*) |
| **Dimension** | Table containing descriptive attributes (dim_*) |
| **VIEW** | Virtual table (no storage, computed on query) |
| **TABLE** | Physical table (stored on disk) |
| **Primary Key** | Unique identifier for a row |
| **Foreign Key** | Reference to primary key in another table |
| **Materialization** | How DBT stores the model (view/table/incremental) |
| **Lineage** | Data flow from source to final table |

---

## Quick Reference - Column Mapping

### How Data Flows Through System

```
orders.json order_id
    ↓ (parse)
raw.orders_raw order_id
    ↓ (cast bigint)
stg_orders order_id
    ↓ (join)
fct_orders order_id
```

```
orders.json user_id
    ↓ (parse)
raw.orders_raw user_id
    ↓ (cast bigint)
stg_orders user_id
    ↓ (join with users)
fct_orders user_id ← stg_users.user_id

users.json username → email
    ↓ (parse)
raw.users_raw user_name ← email
    ↓ (trim, lowercase)
stg_users user_name ← email
    ↓ (join)
fct_orders user_name ← email
```

---

## FAQ - Data Dictionary

**Q: Where does the data come from?**
A: JSON files in `Data_src/` folder are loaded via Python script (`main.py`) into raw tables.

**Q: Can I query raw tables?**
A: Yes, but not recommended for analysis. Use staging/mart tables instead.

**Q: Why use VIEWs for staging?**
A: VIEWs are virtual - they don't consume storage and always reflect the latest raw data.

**Q: How often should I reload data?**
A: Depends on your needs. For this demo, manual loads are typical.

**Q: What's the difference between stg_ and fct_ models?**
A: `stg_` (staging) cleans raw data. `fct_` (fact) combines multiple sources for business logic.

**Q: Can I add new columns?**
A: Yes. Modify SQL files and run `dbt run`.

**Q: Are all null values handled?**
A: Staging and Mart layers require NOT NULL. Check tests if needed.

**Q: How do I know data is fresh?**
A: Check `etl_time` column - it shows when the data was loaded.

---

Last Updated: 2026-03-12
---
