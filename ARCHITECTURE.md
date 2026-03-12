# Architecture Documentation - DBT Demo Project

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  JSON Source Files (Data_src/)                                  │
│    ├── orders.json                                              │
│    └── users.json                                               │
│           ↓                                                       │
│    Python ETL Script (main.py)                                  │
│           ↓                                                       │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PostgreSQL 15 (Analytics Database)                             │
│    ├─ raw schema                                                │
│    │  ├── orders_raw (unprocessed orders)                       │
│    │  └── users_raw (unprocessed users)                         │
│    │                                                             │
│    └─ dbt_dev schema                                            │
│       ├─ stg_orders (cleaned staging view)                      │
│       ├─ stg_users (cleaned staging view)                       │
│       └─ fct_orders (business fact table)                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DBT TRANSFORMATION LAYER                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  DBT Project (dbt_demo/)                                        │
│    ├─ Staging Models (stg_*.sql)                               │
│    │  ├── Type casting                                          │
│    │  ├── Text normalization                                    │
│    │  ├── Column selection                                      │
│    │  └── Materialized as VIEWs                                 │
│    │                                                             │
│    ├─ Mart Models (fct_*.sql)                                  │
│    │  ├── Business logic                                        │
│    │  ├── Joins & enrichment                                    │
│    │  └── Materialized as TABLEs                                │
│    │                                                             │
│    ├─ Data Quality Tests (schema.yml + tests/)                 │
│    │  ├── Built-in tests (not_null, unique, relationships)     │
│    │  └── Custom tests (order_amount_positive.sql)             │
│    │                                                             │
│    └─ Generated Artifacts (target/)                            │
│       ├── manifest.json                                         │
│       ├── compiled/                                             │
│       └── run_results.json                                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ANALYTICS LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Analytics-Ready Data (dbt_dev schema)                          │
│    └── fct_orders: Orders enriched with user info              │
│                                                                   │
│  Ready for:                                                      │
│    ├── BI Tools (Tableau, Power BI, Looker)                    │
│    ├── Direct SQL queries                                       │
│    ├── Data Science & ML pipelines                             │
│    └── Custom reporting                                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Pipeline

### Detailed ETL Flow

```
Stage 1: DATA INGESTION
├── Source: JSON files in Data_src/
│   ├── orders.json (order transactions)
│   └── users.json (user master data)
│
├── Process: main.py Python Script
│   ├── 1. Connect to PostgreSQL
│   ├── 2. Create raw schema (if not exists)
│   ├── 3. Create raw tables (orders_raw, users_raw)
│   ├── 4. Truncate existing data
│   └── 5. Execute bulk insert from JSON
│
└── Output: Unprocessed data in raw schema
    └── raw.orders_raw
    └── raw.users_raw

↓

Stage 2: DATA STAGING (DBT)
├── STG Models: stg_orders.sql & stg_users.sql
│   ├── Type Casting
│   │   └── Ensure correct data types (int, numeric, timestamp)
│   ├── Text Normalization
│   │   ├── Trim whitespace
│   │   └── Lowercase email
│   └── Column Selection
│       └── Keep only relevant columns
│
├── Materialization: VIEWs
│   └── Reason: Data consistency, no storage overhead
│
└── Output: Clean staging views
    ├── dbt_dev.stg_orders
    └── dbt_dev.stg_users

↓

Stage 3: DATA MARTS (DBT)
├── FCT Models: fct_orders.sql
│   ├── Business Logic
│   │   └── Join orders with user details
│   ├── Data Enrichment
│   │   ├── Combine order + user information
│   │   └── Create 360-degree order view
│   └── Aggregations (if needed)
│
├── Materialization: TABLEs
│   └── Reason: Performance, pre-aggregated data
│
└── Output: Analytics-ready fact table
    └── dbt_dev.fct_orders

↓

Stage 4: DATA QUALITY VALIDATION (DBT Tests)
├── Schema Level Tests (schema.yml)
│   ├── NOT NULL checks
│   ├── UNIQUE constraints
│   └── RELATIONSHIPS (FK validation)
│
├── Custom Tests (tests/ folder)
│   └── Business logic validation
│       └── order_amount_positive.sql
│
└── Results: Pass/Fail report
    └── Run tests: dbt test
    └── View results: target/run_results.json
```

---

## Container Architecture

### Docker Compose Structure

```
┌──────────────────────────────────────┐
│      Docker Compose Network          │
│      (Shared bridge network)          │
├──────────────────────────────────────┤
│                                      │
│  ┌──────────────────────────────┐   │
│  │   PostgreSQL Container       │   │
│  │   (postgres:15)              │   │
│  │                              │   │
│  │  - Port: 5432               │   │
│  │  - Volume: postgres_data    │   │
│  │  - Environment:             │   │
│  │    POSTGRES_USER: postgres  │   │
│  │    POSTGRES_PASSWORD: ...   │   │
│  │    POSTGRES_DB: analytics   │   │
│  └──────────────────────────────┘   │
│          ↑                           │
│          │ (Hostname: postgres)     │
│          │                           │
│  ┌──────────────────────────────┐   │
│  │   DBT Container              │   │
│  │   (Custom dbt-postgres)      │   │
│  │                              │   │
│  │  - Volume: ./:/workspace    │   │
│  │  - Volume: profiles.yml     │   │
│  │  - Working: /workspace/...  │   │
│  │  - Environment:             │   │
│  │    DBT_PROFILES_DIR: /root/ │   │
│  │    .dbt                     │   │
│  └──────────────────────────────┘   │
│                                      │
└──────────────────────────────────────┘
```

---

## Component Interaction

### Python ETL ↔ Database

```python
main.py Execution Flow:

1. IMPORT PHASE
   ├── Import json (file reading)
   ├── Import psycopg2 (database connector)
   └── Define DB_CONFIG

2. CONNECTION PHASE
   ├── Create connection to postgres:5432
   └── Establish cursor

3. SCHEMA CREATION
   ├── CREATE SCHEMA raw
   ├── CREATE TABLE raw.orders_raw
   └── CREATE TABLE raw.users_raw

4. DATA LOADING
   ├── Load Data_src/orders.json
   ├── Parse JSON → Python dict list
   ├── INSERT INTO raw.orders_raw
   │
   ├── Load Data_src/users.json
   ├── Parse JSON → Python dict list
   └── INSERT INTO raw.users_raw

5. FINALIZATION
   ├── COMMIT transaction
   └── Close connection
```

### DBT ↔ Database

```sql
dbt Execution Flow:

1. PARSE PHASE
   ├── Read dbt_project.yml
   ├── Read profiles.yml
   ├── Parse all .sql models
   └── Validate syntax

2. COMPILATION PHASE
   ├── Resolve {{ ref() }} macros
   ├── Generate final SQL
   └── Output to target/compiled/

3. EXECUTION PHASE
   ├── RUN stg_orders.sql → CREATE dbt_dev.stg_orders
   ├── RUN stg_users.sql → CREATE dbt_dev.stg_users
   ├── RUN fct_orders.sql → CREATE dbt_dev.fct_orders
   └── Execute in dependency order

4. TESTING PHASE
   ├── Extract test definitions from schema.yml
   ├── Compile test queries
   ├── Execute each test
   └── Report results (Pass/Fail)

5. ARTIFACTS PHASE
   ├── Generate manifest.json
   ├── Generate run_results.json
   └── Store in target/
```

---

## Schema Relationships

### Entity Relationship Diagram (ERD)

```
┌─────────────────────────┐
│     raw.orders_raw      │
├─────────────────────────┤
│ PK: order_id (bigint)   │
│ FK: user_id             │─────────┐
│    total_amount         │         │
│    created_at           │         │
│    etl_time             │         │
└─────────────────────────┘         │
         ↓                           │
    (dbt stg)                       │
         ↓                           │
┌─────────────────────────┐         │
│   dbt_dev.stg_orders    │         │
├─────────────────────────┤         │
│ PK: order_id            │         │
│ FK: user_id             │         │
│    total_amount         │         │
│    created_at           │         │
│    etl_time             │         │
└─────────────────────────┘         │
         ↓ (JOIN)                    │
         │                           │
         └─────────────────────────┐ │
                                   │ │
                                   ↓ ↓
┌─────────────────────────┐ ┌─────────────────────────┐
│   raw.users_raw         │ │  dbt_dev.stg_users      │
├─────────────────────────┤ ├─────────────────────────┤
│ PK: user_id             │ │ PK: user_id             │
│    user_name            │ │    user_name            │
│    email                │ │    email                │
│    created_at           │ │    created_at           │
│    etl_time             │ │    etl_time             │
└─────────────────────────┘ └─────────────────────────┘
         ↓ (dbt stg)
┌─────────────────────────────────────────────┐
│        dbt_dev.fct_orders                    │
├─────────────────────────────────────────────┤
│ PK: order_id                                │
│ FK: user_id                                 │
│    user_name (from stg_users)              │
│    email (from stg_users)                  │
│    total_amount                            │
│    created_at                              │
└─────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Version | Role |
|-------|-----------|---------|------|
| **Runtime** | Docker | 20.10+ | Containerization |
| | Docker Compose | 1.29+ | Orchestration |
| **Database** | PostgreSQL | 15 | OLAP Data Warehouse |
| **ETL** | Python | 3.10 | Data Loading |
| | psycopg2 | 2.9+ | DB Connector |
| **Transformation** | DBT | Latest | Data Modeling |
| | dbt-postgres | Latest | DBT Adapter |
| **Infrastructure** | Linux | Alpine | Container OS |

---

## Data Volume & Performance

### Expected Data Sizes

```
Raw Layer:
  ├── raw.orders_raw: ~10K-100K rows
  ├── raw.users_raw: ~1K-10K rows
  └── Total: ~100 MB (estimated)

Staging Layer:
  ├── stg_orders: ~10K-100K rows (VIEW)
  ├── stg_users: ~1K-10K rows (VIEW)
  └── Storage: 0 MB (virtual, VIEW based)

Mart Layer:
  ├── fct_orders: ~10K-100K rows (TABLE)
  └── Storage: ~10-50 MB (with join)
```

### Performance Characteristics

```
Staging Queries:
  └── Response Time: <100 ms (VIEW overhead minimal)

Mart Queries:
  ├── Count: ~50 ms
  ├── Full scan: ~200 ms
  ├── Filtered: ~20 ms
  └── Joined: ~150 ms

Test Execution:
  ├── Built-in tests: ~5 sec total
  ├── Custom tests: ~2 sec each
  └── Full test suite: ~30 sec
```

---

## Scalability Considerations

### Current Setup (Prototype)

- **Suitable for:** Learning, demos, small datasets (<1M rows)
- **Load frequency:** Manual (daily recommended)
- **Execution time:** < 1 minute

### Scale to Production

```
Scaling Approach:

1. DATA VOLUME
   ├── Increase threads in profiles.yml
   ├── Use incremental materializations
   └── Add database partitioning

2. LOAD FREQUENCY
   ├── Implement airflow/dbt cloud scheduling
   ├── Setup incremental loads
   └── Use dbt Slim CI/CD

3. INFRASTRUCTURE
   ├── Upgrade to managed PostgreSQL (RDS, Cloud SQL)
   ├── Add caching layer (Redis)
   ├── Implement data warehouse (Snowflake, BigQuery)

4. MONITORING
   ├── Setup dbt Cloud monitoring
   ├── Add data quality dashboards
   └── Track performance metrics
```

---

## Error Handling & Recovery

### Main Failure Points

```
1. DATABASE CONNECTION
   └── Recovery: Retry logic with exponential backoff

2. DATA QUALITY
   └── Recovery: DBT tests fail → Stop pipeline

3. TRANSFORMATION LOGIC
   └── Recovery: dbt run --fail-fast → Inspect logs

4. DISK SPACE
   └── Recovery: Monitor postgres_data volume
```

---

## Security Considerations

### Current Setup (Development Only)

```yaml
⚠️ NOT FOR PRODUCTION ⚠️

Hardcoded Credentials:
  DB_CONFIG:
    user: postgres
    password: postgres

Environment Variables:
  POSTGRES_PASSWORD: postgres
```

### Production Recommendations

```yaml
✓ USE FOR PRODUCTION:

1. Environment Variables
   └── export DB_PASSWORD=$(aws secretsmanager ...)

2. Docker Secrets
   └── docker secret create db_password secret.txt

3. External Vault
   └── HashiCorp Vault integration

4. Network Security
   ├── IP whitelisting
   ├── VPC isolation
   └── SSL/TLS connections

5. Database Users
   ├── Separate read/write users
   ├── Row-level security (RLS)
   └── Audit logging
```

---

## Deployment Strategy

### Local Development
```bash
1. Clone repository
2. docker compose up -d --build
3. docker compose exec dbt python /workspace/main.py
4. docker compose exec dbt dbt build
```

### Staging Environment
```bash
1. Push to Git repository
2. Deploy to staging namespace
3. Run full test suite
4. Validate with sample data
```

### Production Deployment
```bash
1. Tag release
2. Build optimized image
3. Deploy to production cluster
4. Run data validation
5. Monitor execution
6. Backup databases
```

---

## Monitoring & Logging

### Log Locations

```
Container Logs:
  ├── dbt logs: dbt_demo/logs/dbt.log
  ├── run results: dbt_demo/target/run_results.json
  ├── postgres logs: docker logs postgres-dbt
  └── dbt container: docker logs dbt-postgres

Database Logs:
  └── PostgreSQL: docker exec postgres-dbt cat /var/log/postgresql/
```

### Metrics to Monitor

```
Data Freshness:
  └── max(etl_time) in raw tables

Data Quality:
  ├── Test pass rate
  ├── Null counts
  └── Duplicate records

Performance:
  ├── Query execution time
  ├── Model build duration
  └── DBT test duration
```

---

## Version Control Strategy

### Git Structure

```
.gitignore
├── dbt_packages/
├── target/
├── logs/
├── .dbt_packages/
└── local_profiles.yml

Tracked:
├── models/
├── tests/
├── dbt_project.yml
├── profiles.yml (template)
├── main.py
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## Disaster Recovery

### Backup Strategy

```bash
# Backup database
docker compose exec postgres-dbt pg_dump -U postgres -d analytics > backup.sql

# Backup DBT artifacts
tar -czf dbt_backup.tar.gz dbt_demo/

# Restore from backup
docker compose exec -T postgres-dbt psql -U postgres -d analytics < backup.sql
```

---

Last Updated: 2026-03-12
