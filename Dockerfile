FROM python:3.10-slim

# Cài các package hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Cài dbt adapters + database drivers
RUN pip install --no-cache-dir \
    dbt-core \
    dbt-postgres \
    dbt-redshift \
    dbt-trino \
    dbt-oracle \
    psycopg2-binary \
    python-dotenv

WORKDIR /usr/app