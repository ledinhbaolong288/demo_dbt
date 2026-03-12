FROM python:3.10-slim

RUN pip install --no-cache-dir dbt-postgres psycopg2-binary python-dotenv

WORKDIR /usr/app