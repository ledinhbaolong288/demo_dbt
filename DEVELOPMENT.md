# Development Guide - DBT Demo Project

## Table of Contents
1. [Development Environment Setup](#development-environment-setup)
2. [Project Development Workflow](#project-development-workflow)
3. [Adding New Models](#adding-new-models)
4. [Writing Tests](#writing-tests)
5. [Debugging & Troubleshooting](#debugging--troubleshooting)
6. [Best Practices](#best-practices)
7. [Common Tasks](#common-tasks)

---

## Development Environment Setup

### Prerequisites

1. **Install Required Software**
   ```bash
   # Docker Desktop (includes Docker and Docker Compose)
   # Download: https://www.docker.com/products/docker-desktop
   
   # Verify installation
   docker --version        # Docker 20.10+
   docker compose --version # Docker Compose 1.29+
   ```

2. **Clone/Download Project**
   ```bash
   cd \Demo\demo_dbt
   ```

3. **Initial Setup**
   ```bash
   # Start services
   docker compose up -d --build
   
   # Verify services
   docker compose ps
   
   # Load data
   docker compose exec dbt python /workspace/main.py
   
   # Build models
   docker compose exec dbt dbt build
   ```

### IDE/Editor Setup

#### Option 1: VS Code
```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[sql]": {
    "editor.defaultFormatter": "dkegel.bracket-pair-colorizer-2"
  }
}
```

**Recommended Extensions:**
- SQL formatter
- YAML formatter
- vscode-icons
- Better Comments

#### Option 2: DataGrip / IntelliJ
```yaml
# Database connection: NOT FOR PRODUCTION
Name: analytics-db
Host: localhost
Port: 5432
Database:
User:
Password:
```

#### Option 3: DBeaver (Free)
- Download: https://dbeaver.io
- Create connection to `localhost:5432`
- Browse schemas and run queries

---

## Project Development Workflow

### Daily Development Cycle

```
1. START OF DAY
   ├── git pull (latest changes)
   ├── docker compose up -d (ensure services running)
   └── docker compose logs (check for errors)

2. DEVELOPMENT
   ├── Create/modify models in models/
   ├── Add tests in schema.yml or tests/
   ├── Run: dbt run (test models)
   ├── Run: dbt test (validate data)
   └── Iterate until passing

3. VERIFICATION
   ├── Query results in database
   ├── Check for data quality issues
   └── Review test coverage

4. COMMIT & PUSH
   ├── git add (modified files)
   ├── git commit (meaningful message)
   └── git push origin (to repository)

5. END OF DAY
   ├── Document changes
   └── Leave services running/stop (your choice)
```

### Git Workflow

```bash
# Start new feature
git checkout -b feature/new-feature

# During development
git add models/path/to/model.sql
git add tests/schema.yml
git commit -m "feat: add new order enrichment model"

# Push to remote
git push origin feature/new-feature

# Create pull request (GitHub/GitLab)
# After approval, merge to main

# Cleanup
git checkout main
git pull
git branch -d feature/new-feature
```

---

## Adding New Models

### Step 1: Create SQL Model File

```bash
# Create file in appropriate folder
# models/staging/stg_new_entity.sql
# models/marts/fct_new_concept.sql
```

### Step 2: Write Model SQL

```sql
-- models/staging/stg_new_entity.sql

{{
  config(
    materialized='view',  -- or 'table'
    tags=['staging', 'critical']
  )
}}

select
    cast(id as bigint) as id,
    cast(name as varchar) as name,
    cast(created_at as timestamp) as created_at
from raw.new_entity_raw
where deleted_at is null
```

### Step 3: Add Tests in schema.yml

```yaml
# models/schema.yml

models:
  - name: stg_new_entity
    description: "Cleaned staging layer for new_entity"
    columns:
      - name: id
        description: "Primary key"
        tests:
          - not_null
          - unique
      
      - name: name
        description: "Entity name"
        tests:
          - not_null
```

### Step 4: Test the Model

```bash
# Enter dbt container
docker compose exec dbt bash

# Parse syntax
dbt parse

# Run model
dbt run -s stg_new_entity

# Test model
dbt test -s stg_new_entity

# Full build
dbt build -s stg_new_entity

# Exit container
exit
```

### Step 5: Verify Results

```bash
# Query in database
docker exec -it postgres-dbt psql -U postgres -d analytics

-- View staging model results
select * from dbt_dev.stg_new_entity limit 10;

-- Check row count
select count(*) from dbt_dev.stg_new_entity;
```

---

## Model Structure Examples

### Example 1: Simple Staging Model

```sql
-- models/staging/stg_products.sql

{{
  config(
    materialized='view',
    tags=['staging']
  )
}}

select
    cast(product_id as bigint) as product_id,
    trim(product_name) as product_name,
    cast(price as numeric(18,2)) as price,
    cast(created_at as timestamp) as created_at
from raw.products_raw
where product_id is not null
```

### Example 2: Fact Table with Joins

```sql
-- models/marts/fct_sales.sql

{{
  config(
    materialized='table',
    tags=['marts', 'core']
  )
}}

select
    s.sale_id,
    s.product_id,
    s.customer_id,
    p.product_name,
    c.customer_name,
    c.email,
    s.quantity,
    s.unit_price,
    (s.quantity * s.unit_price) as sale_amount,
    s.sale_date
from {{ ref('stg_sales') }} s
left join {{ ref('stg_products') }} p
    on s.product_id = p.product_id
left join {{ ref('stg_customers') }} c
    on s.customer_id = c.customer_id
```

### Example 3: Incremental Model

```sql
-- models/marts/fct_daily_sales.sql

{{
  config(
    materialized='incremental',
    unique_key='sale_date',
    tags=['marts', 'incremental']
  )
}}

select
    cast(sale_date as date) as sale_date,
    count(*) as transaction_count,
    sum(sale_amount) as daily_revenue
from {{ ref('fct_sales') }}
{% if execute %}
    where sale_date > (select max(sale_date) from {{ this }})
{% endif %}
group by cast(sale_date as date)
```

### Example 4: Model with Descriptions

```sql
-- models/staging/stg_customers.sql
-- Provides cleaned customer data from raw source
-- Applies data quality rules:
--   - Removes deleted customers
--   - Normalizes email addresses
--   - Standardizes phone formats

{{
  config(
    materialized='view',
    tags=['staging', 'customers'],
    meta={'owner': 'analytics_team'}
  )
}}

select
    customer_id,
    customer_name,
    lower(email) as email,
    country_code
from raw.customers_raw
where deleted_at is null
```

---

## Writing Tests

### Built-in Tests (schema.yml)

```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      
      - name: user_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_users')
              field: user_id
      
      - name: total_amount
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 1000000
```

### Custom Tests

#### File-Based Test

```sql
-- tests/assert_order_amounts_positive.sql
-- Checks that all orders have positive amounts

select *
from {{ ref('fct_orders') }}
where total_amount <= 0
```

#### Generic Test

```sql
-- tests/generic/test_no_future_dates.sql
-- Ensures date column doesn't contain future dates

{% test no_future_dates(model, column_name) %}

select *
from {{ model }}
where {{ column_name }} > current_date

{% endtest %}
```

Usage in schema.yml:
```yaml
models:
  - name: fct_orders
    columns:
      - name: created_at
        tests:
          - no_future_dates
```

### Running Tests

```bash
docker compose exec dbt bash

# Run all tests
dbt test

# Run tests for specific model
dbt test -s stg_orders

# Run tests with verbose output
dbt test --debug

# Run specific test
dbt test -s test_order_amounts_positive

# Exit
exit
```

---

## Debugging & Troubleshooting

### 1. Model Compilation Errors

```bash
# Debug parse errors
docker compose exec dbt dbt parse

# Debug with verbose logging
docker compose exec dbt dbt run --debug

# Check logs
cat dbt_demo/logs/dbt.log
```

**Common Issues:**

```
Error: Couldn't find model 'unknown_model'
→ Check {{ ref() }} references are correct

Error: Column 'xxx' not found in source
→ Check source table has the column
→ Query raw table directly

Error: Type casting failed
→ Check actual data types in raw table
→ Adjust cast() function
```

### 2. Test Failures

```bash
# Run single test with details
docker compose exec dbt dbt test -s stg_orders --debug

# Generate test query without executing
docker compose exec dbt dbt test -s stg_orders --debug --store-failures

# Check test results
docker compose exec -it postgres-dbt psql -U postgres -d analytics
select * from dbt_test__audit;
```

**Common Test Issues:**

```sql
-- NOT NULL test failed
select count(*) from {{ ref('model_name') }} 
where column_name is null;

-- UNIQUE test failed
select column_name, count(*) cnt 
from {{ ref('model_name') }} 
group by column_name 
having count(*) > 1;

-- RELATIONSHIP test failed
select * from {{ ref('model_name') }} 
where foreign_key not in (
    select primary_key from {{ ref('ref_model') }}
);
```

### 3. Data Quality Issues

```bash
# Connect to database
docker exec -it postgres-dbt psql -U postgres -d analytics

-- Check source data volume
select count(*) from raw.orders_raw;
select count(*) from raw.users_raw;

-- Check staging results
select count(*) from dbt_dev.stg_orders;
select distinct user_id from dbt_dev.fct_orders;

-- Find nulls
select * from dbt_dev.fct_orders where user_id is null;

-- Find duplicates
select order_id, count(*) cnt 
from dbt_dev.fct_orders 
group by order_id 
having count(*) > 1;
```

### 4. Performance Issues

```bash
# Profile model execution
docker compose exec dbt dbt run --profiles-dir profiles --debug

# Check execution stats
cat dbt_demo/target/run_results.json | grep -A5 '"execution_time"'

# Add indexes for frequently joined columns
docker exec -it postgres-dbt psql -U postgres -d analytics

CREATE INDEX idx_stg_orders_user_id ON dbt_dev.stg_orders(user_id);
CREATE INDEX idx_fct_orders_user_id ON dbt_dev.fct_orders(user_id);
```

### 5. Container Issues

```bash
# View container status
docker compose ps

# View logs
docker compose logs -f dbt
docker compose logs -f postgres

# Restart services
docker compose restart

# Rebuild from scratch
docker compose down -v
docker compose up -d --build

# Get container details
docker compose ps --services
docker compose config
```

---

## Best Practices

### 1. Naming Conventions

```
Staging Models:
  ├── stg_{source}_{entity}.sql
  ├── Example: stg_salesforce_accounts.sql
  └── Example: stg_web_events.sql

Fact Tables:
  ├── fct_{concept}.sql
  ├── Example: fct_orders.sql
  └── Example: fct_customer_lifetime_value.sql

Dimension Tables:
  ├── dim_{concept}.sql
  ├── Example: dim_customers.sql
  └── Example: dim_products.sql

Tests:
  ├── test_{check_type}_{model}.sql
  ├── Example: test_no_future_dates_orders.sql
  └── Example: test_orders_amount_positive.sql
```

### 2. File Organization

```
models/
├── staging/
│   ├── stg_orders.sql
│   ├── stg_users.sql
│   └── _stg_staging.yml
├── marts/
│   ├── fct_orders.sql
│   └── _marts.yml
├── intermediate/ (optional)
│   ├── int_order_summary.sql
│   └── _intermediate.yml
└── schema.yml  # or split by folder
```

### 3. SQL Style Guide

```sql
-- Bad
select order_id,user_id,total_amount,created_at from raw.orders_raw where active='T'

-- Good ✓
select
    order_id,
    user_id,
    total_amount,
    created_at
from raw.orders_raw
where active = 'true'
```

### 4. Documentation

```sql
-- Always add descriptions
models:
  - name: fct_orders
    description: |
      Orders fact table containing all order transactions.
      Joins base orders with customer details.
      Grain: One row per order.
    
    columns:
      - name: order_id
        description: "Unique order identifier (PK)"
        tests:
          - unique
          - not_null
      
      - name: user_id
        description: "User who placed the order (FK to dim_users)"
        tests:
          - not_null
          - relationships:
              to: ref('stg_users')
              field: user_id
```

### 5. Testing Strategy

```
Minimum Testing Requirements:

Staging Models:
  ├── Primary keys: unique + not_null
  ├── Foreign keys: relationships tests
  └── Critical columns: not_null tests

Fact Tables:
  ├── Primary keys: unique + not_null
  ├── Foreign keys: relationships tests
  ├── All columns: not_null (unless expected)
  └── Business logic: custom tests

Data Quality Target: 80%+ column coverage
```

### 6. Code Review Checklist

```
Before committing:
  ☐ All tests pass (dbt test)
  ☐ Model builds successfully (dbt run)
  ☐ Naming follows conventions
  ☐ Added descriptions in schema.yml
  ☐ SQL is formatted consistently
  ☐ Removed debug prints/comments
  ☐ No hardcoded values
  ☐ Uses {{ ref() }} for dependencies
  ☐ Appropriate materialization type
  ☐ Documented complex logic
```

---

## Common Tasks

### Task 1: Add a New Source

```yaml
# models/schema.yml
version: 2

sources:
  - name: raw
    description: "Raw data schema"
    database: analytics
    schema: raw
    tables:
      - name: orders_raw
        columns:
          - name: order_id
            tests:
              - unique
              - not_null
```

Use in model:
```sql
select * from {{ source('raw', 'orders_raw') }}
```

### Task 2: Modify Existing Model

```bash
# Edit model file
vim models/staging/stg_orders.sql

# Test changes
docker compose exec dbt dbt run -s stg_orders

# Run dependent models
docker compose exec dbt dbt run -s +stg_orders

# Test everything
docker compose exec dbt dbt test
```

### Task 3: Add Documentation

```yaml
# models/schema.yml
models:
  - name: fct_orders
    description: |
      Orders fact table with complete order and customer information.
      
      ### Grain
      One row per order transaction.
      
      ### Transformations
      - Joins stg_orders with stg_users
      - Enriches with customer contact details
      - Validates all amounts are positive
    
    columns:
      - name: order_id
        description: "Unique order identifier"
```

### Task 4: Add Data Test

```sql
-- tests/assert_order_total_reasonable.sql
-- Business logic: Order totals should be between $1 and $100,000

select *
from {{ ref('fct_orders') }}
where total_amount < 1 or total_amount > 100000
```

Run:
```bash
docker compose exec dbt dbt test -s assert_order_total_reasonable
```

### Task 5: Regenerate Models

```bash
# Full rebuild (delete and recreate)
docker compose exec dbt dbt run --full-refresh

# Rebuild specific model
docker compose exec dbt dbt run -s fct_orders --full-refresh

# Rebuild model + dependents
docker compose exec dbt dbt run -s fct_orders+ --full-refresh
```

### Task 6: Check Model Dependencies

```bash
# View dependency graph
docker compose exec dbt dbt parse

# Find model lineage
docker compose exec dbt dbt ls -s fct_orders   # Direct dependencies
docker compose exec dbt dbt ls -s fct_orders+  # Downstream
docker compose exec dbt dbt ls -s +fct_orders  # Upstream
```

### Task 7: Generate Documentation

```bash
# Generate docs
docker compose exec dbt dbt docs generate

# Serve docs locally
docker compose exec dbt dbt docs serve

# Access: http://localhost:8000
```

---

## Performance Optimization

### 1. Query Performance

```sql
-- Bad: Full table scan
select * from fct_orders where user_id = 123

-- Good: Uses index
select user_id, order_id, total_amount
from fct_orders
where user_id = 123
```

### 2. Model Materialization

```yaml
# Use appropriate materialization:

staging:
  +materialized: view        # Virtual, no storage
  
marts:
  +materialized: table       # Physical, indexed

incremental_marts:
  +materialized: incremental # Only new data
```

### 3. Parallel Execution

```yaml
# profiles.yml
outputs:
  dev:
    threads: 8  # Increase from 4
```

---

## Useful Commands Quick Reference

```bash
# Development shell
docker compose exec dbt bash

# Within dbt container:

# Parse and validate
dbt parse
dbt parse --debug

# Run models
dbt run                           # Run all
dbt run -s model_name             # Run specific
dbt run -s model_name+            # Run + downstream
dbt run -s +model_name            # Run + upstream

# Test
dbt test                          # Test all
dbt test -s model_name            # Test specific

# Build (run + test)
dbt build
dbt build -s model_name           # Build specific

# Documentation
dbt docs generate
dbt docs serve

# Debug
dbt debug
dbt depsn show                     # Dependency graph
dbt ls                            # List models
dbt list -s tag:critical          # Filter by tag

# Cleanup
exit                              # Exit dbt container
```

---

Last Updated: 2026-03-12
