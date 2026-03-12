# Quick Start Guide - DBT Demo Project

Get the project running in 5 minutes!

## Prerequisites

Before starting, ensure you have:
- ✓ Docker Desktop installed and running
- ✓ Docker Compose installed (included with Docker Desktop)
- ✓ Project folder: `\Demo\demo_dbt`
- ✓ ~5 GB free disk space

## Step-by-Step Setup

### Step 1: Open Terminal

```bash
# Windows PowerShell
cd Demo\demo_dbt
```

### Step 2: Start Services (1 minute)

```bash
docker compose up -d --build
```

**Expected output:**
```
[+] Building 12.3s
[+] Creating postgres-dbt  1/1 ✓
[+] Creating dbt-postgres  1/1 ✓
```

Verify services are running:
```bash
docker compose ps
```

Should show:
```
NAME            STATUS
postgres-dbt    Up 20 seconds
dbt-postgres    Up 15 seconds
```

### Step 3: Load Data (1 minute)

```bash
docker compose exec dbt python /workspace/main.py
```

**Expected output:**
```
Raw tables created and data loaded successfully!
```

### Step 4: Build Models (2 minutes)

```bash
docker compose exec dbt dbt build
```

**Expected output:**
```
Completed successfully

Done. PASS: X runs, X tests in 45.32s
```

### Step 5: Query Results (1 minute)

```bash
docker exec -it postgres-dbt psql -U postgres -d analytics
```

In the psql prompt:
```sql
-- View transformed data
select * from dbt_dev.fct_orders limit 5;

-- Count records
select count(*) from dbt_dev.fct_orders;

-- Exit psql
\q
```

**Done! 🎉**

---

## Verify Everything Works

### Health Check

```bash
# Check all containers running
docker compose ps

# Check logs for errors
docker compose logs

# Test database connectivity
docker compose exec -it postgres-dbt psql -U postgres -d analytics -c "select current_database();"
```

### Data Validation

```sql
-- From psql console
-- Expected: Raw data with nulls possible
select count(*) as raw_orders from raw.orders_raw;

-- Expected: Cleaned data, no nulls
select count(*) as staging_orders from dbt_dev.stg_orders;

-- Expected: Same count as raw
select count(*) as mart_orders from dbt_dev.fct_orders;

-- Exit
\q
```

---

## Common Commands Reference

### Start/Stop

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Stop and remove all data
docker compose down -v
```

### Development

```bash
# Enter dbt container
docker compose exec dbt bash

# Inside container:
dbt run           # Build models
dbt test          # Run tests
dbt build         # Run + test
exit              # Exit container
```

### Database

```bash
# Connect to database
docker exec -it postgres-dbt psql -U postgres -d analytics

# Useful psql commands:
# \dn              List schemas
# \dt              List tables
# \dt raw.*        List tables in raw schema
# select * from raw.orders_raw;  Query
# \q               Exit
```

### Logs

```bash
# View all logs
docker compose logs

# View dbt logs
docker compose logs dbt

# View postgres logs
docker compose logs postgres

# Follow logs (live)
docker compose logs -f
```

---

## Next Steps

### For Beginners
1. ✓ Complete this Quick Start
2. → Read [README.md](README.md) for full documentation
3. → Explore [DATA_DICTIONARY.md](DATA_DICTIONARY.md) to understand the data

### For Developers
1. ✓ Complete this Quick Start
2. → Follow [DEVELOPMENT.md](DEVELOPMENT.md) for development workflow
3. → Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design

### For DevOps/Deployment
1. ✓ Complete this Quick Start
2. → Read deployment best practices (in README.md)
3. → Configure production environment

---

## Troubleshooting

### Services Won't Start

```bash
# Full cleanup and restart
docker compose down -v
docker compose up -d --build

# If still failing, check Docker
docker --version
docker run hello-world
```

### Port Already in Use

```bash
# Windows: Find and kill process using port 5432
netstat -ano | findstr :5432
taskkill /PID <PID_NUMBER> /F

# Alternative: Change port in docker-compose.yml
# ports:
#   - "5433:5432"  # Use 5433 instead
```

### Data Load Failed

```bash
# Check if container is running
docker compose ps dbt

# Check Python path
docker compose exec dbt python -c "import psycopg2; print('OK')"

# Run with verbose output
docker compose exec dbt python /workspace/main.py -v
```

### Models Won't Build

```bash
# Verify dbt can connect
docker compose exec dbt dbt debug

# Parse models
docker compose exec dbt dbt parse

# Check for SQL errors
docker compose exec dbt dbt run --debug
```

---

## Explore Data

### Query Examples

```sql
-- Total orders
select count(*) as total_orders from dbt_dev.fct_orders;

-- Orders by user
select user_name, count(*) as order_count
from dbt_dev.fct_orders
group by user_name
order by order_count desc;

-- Revenue analysis
select 
    user_name,
    count(*) as orders,
    sum(total_amount) as total_spent,
    avg(total_amount) as avg_order_value
from dbt_dev.fct_orders
group by user_name
order by total_spent desc;

-- Recent orders
select order_id, user_name, email, total_amount, created_at
from dbt_dev.fct_orders
where created_at >= current_date - interval '7 days'
order by created_at desc;
```

---

## Project Structure Overview

```
Project Root (\Demo\demo_dbt)
├── README.md              ← Full documentation
├── ARCHITECTURE.md        ← System design
├── DEVELOPMENT.md         ← Dev guide
├── DATA_DICTIONARY.md     ← Data reference
├── docker-compose.yml     ← Services config
├── Dockerfile             ← DBT container
├── main.py               ← Data loader
├── profiles.yml          ← DBT connection
├── Data_src/             ← Source files (JSON)
└── dbt_demo/             ← DBT project
    ├── dbt_project.yml
    ├── models/           ← SQL transformations
    ├── tests/            ← Data validation
    └── target/           ← Build output
```

---

## Key Files to Know

| File | Purpose |
|------|---------|
| docker-compose.yml | Defines PostgreSQL + DBT containers |
| main.py | Loads JSON data into raw tables |
| dbt_demo/models/ | SQL transformation models |
| dbt_demo/dbt_project.yml | DBT project settings |
| profiles.yml | Database connection config |

---

## Success Indicators

✓ You've succeeded when:
1. `docker compose ps` shows 2 containers running
2. `docker compose exec dbt dbt build` completes with "Done"
3. `select * from dbt_dev.fct_orders;` returns data

---

## Getting Help

| Issue | Solution |
|-------|----------|
| Can't find file | Check working directory: `cd \Demo\demo_dbt` |
| Docker not starting | Download Docker Desktop: https://www.docker.com/products/docker-desktop |
| Python errors | Check main.py by reading [README.md](README.md#python-data-loading) |
| DBT errors | Check logs: `docker compose logs dbt` |
| Data missing | Reload: `docker compose exec dbt python /workspace/main.py` |

---

## Documentation Map

```
Quick Start (You are here!)
    ↓
README.md (Full Overview)
    ├─→ ARCHITECTURE.md (How it works)
    ├─→ DEVELOPMENT.md (How to develop)
    ├─→ DATA_DICTIONARY.md (What the data contains)
    └─→ DEPLOYMENT.md (Production setup)
```

---

**Next:** Read [README.md](README.md) for comprehensive documentation

**Time to complete:** 5 minutes
**Last updated:** 2026-03-12
