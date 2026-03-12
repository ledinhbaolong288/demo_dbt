# Troubleshooting Guide - DBT Demo Project

Common issues and solutions.

## Table of Contents
1. [Docker & Container Issues](#docker--container-issues)
2. [Database Connection Issues](#database-connection-issues)
3. [Data Loading Issues](#data-loading-issues)
4. [DBT Model Issues](#dbt-model-issues)
5. [Test Failures](#test-failures)
6. [Performance Issues](#performance-issues)
7. [FAQs](#faqs)

---

## Docker & Container Issues

### Issue: Docker daemon not running

**Symptom:**
```
error during connect: This error may indicate the docker daemon is not running.
```

**Solution:**
```bash
# Windows: Start Docker Desktop application
# Or use terminal:
wsl --install
docker run hello-world  # Verify working
```

### Issue: Port 5432 already in use

**Symptom:**
```
Error response from daemon: driver failed programming external connectivity on 
endpoint postgres-dbt: Ports are not available: exposing port TCP 0.0.0.0:5432
```

**Solution 1: Find and kill the process**
```bash
# Find process using port 5432
netstat -ano | findstr :5432

# Kill process (replace PID with actual PID)
taskkill /PID 1234 /F

# Restart Docker
docker compose down
docker compose up -d
```

**Solution 2: Change port in docker-compose.yml**
```yaml
services:
  postgres:
    ports:
      - "5433:5432"  # Change from 5432:5432
```

Then update `profiles.yml`:
```yaml
port: 5433  # Change from 5432
```

### Issue: Insufficient disk space

**Symptom:**
```
no space left on device
```

**Solution 1: Clean up Docker**
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused containers
docker container prune

# Full cleanup
docker system prune -a --volumes
```

**Solution 2: Rebuild with minimal storage**
```bash
# Stop and remove
docker compose down -v

# Rebuild
docker compose up -d --build
```

### Issue: Containers keep crashing

**Symptom:**
```
Container exited with status 1
```

**Solution:**
```bash
# View detailed logs
docker compose logs postgres
docker compose logs dbt

# Restart services
docker compose restart

# Full rebuild
docker compose down
docker compose up -d --build

# Check service health
docker compose ps
```

---

## Database Connection Issues

### Issue: Cannot connect to PostgreSQL

**Symptom:**
```
psycopg2.OperationalError: could not connect to server: 
Connection refused. Is the server running?
```

**Solution 1: Verify PostgreSQL is running**
```bash
# Check status
docker compose ps

# Output should show postgres container "Up"

# If not running, start it
docker compose up -d postgres
```

**Solution 2: Verify connection settings**
```bash
# From Windows PowerShell
docker compose exec postgres-dbt psql -U postgres -d analytics -c "select 1;"

# Should output: ?column?
#      1
```

**Solution 3: Check network connectivity**
```bash
# From dbt container
docker compose exec dbt bash
ping postgres
exit

# Should show: postgres is reachable
```

### Issue: Authentication failed

**Symptom:**
```
FATAL: password authentication failed for user "postgres"
```

**Solution:**
```bash
# Verify credentials in profiles.yml
cat profiles.yml

# Should show:
# user: postgres
# password: postgres

# Check environment variables
docker compose config | grep POSTGRES

# If wrong, recreate container
docker compose down -v
docker compose up -d --build
```

### Issue: Database doesn't exist

**Symptom:**
```
FATAL: database "analytics" does not exist
```

**Solution:**
```bash
# Verify database was created
docker exec -it postgres-dbt psql -U postgres -l

# Look for "analytics" in list

# If missing, create it
docker exec -it postgres-dbt psql -U postgres -c "CREATE DATABASE analytics;"

# Recreate services
docker compose down -v
docker compose up -d --build
```

---

## Data Loading Issues

### Issue: main.py fails to run

**Symptom:**
```
Error: main.py not found or ModuleNotFoundError
```

**Solution:**
```bash
# Verify file exists
ls -la main.py

# Verify it's in correct location
docker compose exec dbt ls -la /workspace/

# Run with full path
docker compose exec dbt python /workspace/main.py

# Check Python version
docker compose exec dbt python --version
```

### Issue: JSON files not found

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'Data_src/orders.json'
```

**Solution:**
```bash
# Verify files exist
ls -la Data_src/

# Should show: orders.json, users.json

# Verify JSON is valid
python -m json.tool Data_src/orders.json

# If broken JSON, check file
cat Data_src/orders.json | head -20
```

### Issue: Data import is very slow

**Symptom:**
```
Script running for >5 minutes
```

**Solution:**
```bash
# Check file sizes
ls -lh Data_src/

# Check database storage
docker compose exec postgres-dbt du -sh /var/lib/postgresql/data/

# Monitor in background
docker compose exec -d dbt python /workspace/main.py

# Check progress
docker compose logs -f dbt
```

### Issue: Duplicate data after reload

**Symptom:**
```
INSERT fails with unique constraint violation
Row count keeps increasing
```

**Solution:**
```bash
# Truncate tables before insert (main.py does this)
docker compose exec postgres-dbt psql -U postgres -d analytics -c "TRUNCATE TABLE raw.orders_raw CASCADE;"
docker compose exec postgres-dbt psql -U postgres -d analytics -c "TRUNCATE TABLE raw.users_raw CASCADE;"

# Then reload
docker compose exec dbt python /workspace/main.py
```

---

## DBT Model Issues

### Issue: dbt parse fails

**Symptom:**
```
ERROR: Runtime Error while parsing dbt_project.yml
```

**Solution:**
```bash
# Validate YAML syntax
docker compose exec dbt bash

# Inside container:
python -m yaml dbt_project.yml
dbt parse --debug

# Check file structure
cat dbt_project.yml
exit
```

### Issue: Model references are broken

**Symptom:**
```
ERROR: Couldn't find model 'unknown_model'
```

**Solution:**
```bash
# Check all available models
docker compose exec dbt dbt ls

# Verify {{ ref() }} in SQL
docker compose exec dbt grep -r "ref(" models/

# Full path example:
# models/staging/stg_orders.sql → use ref('stg_orders')
# models/marts/fct_orders.sql → use ref('fct_orders')

# Rerun parse
docker compose exec dbt dbt parse
```

### Issue: Circular dependency error

**Symptom:**
```
ERROR: Circular dependency detected
```

**Solution:**
```
Check model dependencies:
  stg_orders → uses raw.orders_raw only
  stg_users → uses raw.users_raw only
  fct_orders → uses stg_orders + stg_users

INCORRECT (creates circle):
  stg_orders → fct_orders
  fct_orders → stg_orders  ✗

FIX: Only raw tables should reference {{ ref() }}
```

### Issue: Model compiled but wrong SQL

**Symptom:**
```
Query returns unexpected results
```

**Solution:**
```bash
# View compiled SQL
cat dbt_demo/target/compiled/dbt_demo/models/staging/stg_orders.sql

# View raw SQL in source
cat dbt_demo/models/staging/stg_orders.sql

# Test individual statement
docker compose exec postgres-dbt psql -U postgres -d analytics

-- Copy the compiled SQL and execute manually
-- Check if source table has the data
select * from raw.orders_raw limit 5;

\q
```

### Issue: dbt run out of memory

**Symptom:**
```
ERROR: std::bad_alloc or MemoryError
```

**Solution:**
```bash
# Increase Docker memory allocation
# Edit docker-compose.yml:

services:
  dbt:
    mem_limit: 2g      # Add this line

# Rebuild
docker compose down
docker compose up -d --build

# Or on command line:
docker run --memory=2g ...
```

---

## Test Failures

### Issue: Tests are failing

**Symptom:**
```
Failures
  2 of 5 tests FAIL
```

**Solution 1: Run tests individually**
```bash
docker compose exec dbt dbt test -s stg_orders --debug
```

**Solution 2: Check test SQL**
```bash
# View test query
cat dbt_demo/target/compiled/.../test_*.sql

# Run test query manually
docker exec -it postgres-dbt psql -U postgres -d analytics

-- Run the test query
select * from [table] where [condition];

-- If returns rows = test FAILED
-- If returns 0 rows = test PASSED
```

### Issue: not_null test fails

**Symptom:**
```
TEST FAILED: not_null on column ORDER_ID
```

**Solution:**
```sql
-- Find null values
select * from dbt_dev.stg_orders where order_id is null;

-- Delete or fix null rows
delete from raw.orders_raw where order_id is null;

-- Reload data
docker compose exec dbt python /workspace/main.py

-- Rerun tests
docker compose exec dbt dbt test
```

### Issue: unique test fails

**Symptom:**
```
TEST FAILED: unique constraint on USER_ID
```

**Solution:**
```sql
-- Find duplicates
select user_id, count(*) as cnt 
from dbt_dev.stg_users 
group by user_id 
having count(*) > 1;

-- Delete duplicates
delete from raw.users_raw 
where user_id in (
    select user_id from [duplicates list]
);

-- Reload
docker compose exec dbt python /workspace/main.py
```

### Issue: relationships test fails

**Symptom:**
```
TEST FAILED: relationships on USER_ID
Invalid references
```

**Solution:**
```sql
-- Find orphaned records
select o.* from dbt_dev.stg_orders o
left join dbt_dev.stg_users u on o.user_id = u.user_id
where u.user_id is null;

-- Delete orphaned records
delete from raw.orders_raw 
where user_id not in (select user_id from raw.users_raw);

-- Reload
docker compose exec dbt python /workspace/main.py
```

---

## Performance Issues

### Issue: dbt run is very slow

**Solution 1: Increase threads**
```yaml
# profiles.yml
outputs:
  dev:
    threads: 8  # Increase from 4
```

**Solution 2: Check query execution**
```bash
docker compose exec dbt dbt run --debug
docker compose logs postgres
```

**Solution 3: Add database indexes**
```sql
CREATE INDEX idx_orders_user_id ON raw.orders_raw(user_id);
CREATE INDEX idx_fct_orders_created_at ON dbt_dev.fct_orders(created_at);
```

### Issue: Query timeout

**Symptom:**
```
Connection timeout
Cancelling query due to timeout
```

**Solution:**
```bash
# Increase timeout in profiles.yml
port: 5432
timeout_seconds: 300  # Add this

# Or limit query size
docker compose exec dbt dbt run -s model_name  # Run one model at a time
```

### Issue: High memory usage

**Solution:**
```bash
# Monitor usage
docker stats

# Limit container memory
docker update --memory 2g postgres-dbt
docker update --memory 2g dbt-postgres

# Rebuild
docker compose down
docker compose up -d --build
```

---

## FAQs

### Q: How do I completely reset everything?

**A:**
```bash
# Stop all services
docker compose down

# Remove all data
docker compose down -v

# Remove images
docker rmi postgres:15
docker rmi dbt-postgres

# Rebuild
docker compose up -d --build

# Reload data
docker compose exec dbt python /workspace/main.py
```

### Q: Can I backup my database?

**A:**
```bash
# Backup
docker compose exec postgres-dbt pg_dump -U postgres analytics > backup.sql

# Restore
docker compose exec -T postgres-dbt psql -U postgres analytics < backup.sql
```

### Q: How do I access the database from outside containers?

**A:**
Use connection string:
```
Host: localhost
Port: 5432
Database: analytics
User: postgres
Password: postgres
```

Tools: DBeaver, pgAdmin, DataGrip, VS Code SQL extension

### Q: Can I run dbt from my local machine (not Docker)?

**A:**
Yes, but requires:
```bash
# Install dbt-postgres locally
pip install dbt-postgres==1.x.x

# Update profiles.yml to point to localhost:5432

# Run commands
dbt run
dbt test
dbt build
```

### Q: How do I add new data without reloading everything?

**A:**
Modify `main.py` to use UPSERT instead of TRUNCATE:
```python
# Instead of truncate:
# cur.execute("TRUNCATE TABLE raw.orders_raw;")

# Use INSERT with ON CONFLICT:
cur.execute("""
    INSERT INTO raw.orders_raw (order_id, user_id, total_amount, created_at)
    VALUES %s
    ON CONFLICT (order_id) DO UPDATE SET
        total_amount = EXCLUDED.total_amount,
        updated_at = NOW()
""", rows)
```

### Q: What are typical error codes?

**A:**
```
0   = Success
1   = General error
2   = Misuse of command
126 = Cannot execute
127 = Command not found
Connection refused = Database not running
```

### Q: How do I view dbt documentation?

**A:**
```bash
docker compose exec dbt dbt docs generate
docker compose exec dbt dbt docs serve

# Open browser: http://localhost:8000
```

---

## Getting More Help

### Check Logs at Each Stage

```bash
# 1. Service startup
docker compose logs postgres
docker compose logs dbt

# 2. Data loading
docker compose logs --tail 100 dbt

# 3. Model execution
cat dbt_demo/logs/dbt.log

# 4. Test execution
cat dbt_demo/target/run_results.json

# 5. Database activity
docker exec postgres-dbt tail -f /var/log/postgresql/postgresql.log
```

### Debug Mode

```bash
# Enable debug logging
docker compose exec dbt dbt run --debug

# Save debug output
docker compose exec dbt dbt run --debug > debug.log 2>&1

# Review log
cat debug.log
```

### Test on Smallest Dataset

```bash
# Reduce source data for testing
# Edit Data_src/orders.json to have 10 rows only
# Run pipeline
docker compose exec dbt python /workspace/main.py
docker compose exec dbt dbt build

# If works, issue is with data volume
# If fails, issue is with logic
```

---

## Contact & Escalation

If issue not resolved:
1. Check all steps in this guide
2. Review logs completely
3. Try full reset: `docker compose down -v`
4. Rebuild from scratch: `docker compose up -d --build`
5. Document error and share:
   - Error message (full text)
   - Command that failed
   - Logs from `docker compose logs`
   - Operating system and Docker version

---

Last Updated: 2026-03-12
