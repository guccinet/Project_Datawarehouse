"""
Piwat Data Warehouse — Automated Medallion ETL Pipeline
======================================================
Daily orchestration pipeline executing incremental extraction,
transformation into Bronze/Silver/Gold layers, and BI synchronization.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator

default_args = {
    "owner": "piwat-data-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=3),
}

with DAG(
    dag_id="piwat_daily_etl",
    default_args=default_args,
    description="Medallion Data Warehouse Pipeline (Bronze -> Silver -> Gold)",
    schedule="0 19 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["piwat", "lakehouse", "medallion", "postgresql"],
    max_active_runs=1,
) as dag:

    # 1. Pipeline Lifecycle Inception
    pipeline_init = EmptyOperator(task_id="pipeline_init")

    # 2. Source Data Extraction (PostgreSQL OLTP)
    extract_sales = EmptyOperator(task_id="extract_postgres_sales")
    extract_inventory = EmptyOperator(task_id="extract_postgres_inventory")
    extract_logistics = EmptyOperator(task_id="extract_postgres_logistics")

    # 3. Bronze Layer Ingestion (Raw Snapshot Landing)
    load_bronze_layer = EmptyOperator(task_id="load_bronze_lakehouse")

    # 4. Silver Layer Transformation (Validation, Deduplication & Typing)
    transform_silver_orders = EmptyOperator(task_id="transform_silver_orders")
    transform_silver_inventory = EmptyOperator(task_id="transform_silver_inventory")

    # 5. Gold Layer Star Schema Modeling
    build_gold_dimensions = EmptyOperator(task_id="build_gold_dimensions")
    build_gold_fact_sales = EmptyOperator(task_id="build_gold_fact_sales")

    # 6. Data Quality Audit & BI Notification
    validate_data_quality = EmptyOperator(task_id="validate_data_quality")
    refresh_superset_cache = EmptyOperator(task_id="refresh_superset_cache")
    pipeline_completed = EmptyOperator(task_id="pipeline_completed")

    # Orchestration Flow Graph
    pipeline_init >> [extract_sales, extract_inventory, extract_logistics]
    [extract_sales, extract_inventory, extract_logistics] >> load_bronze_layer
    load_bronze_layer >> [transform_silver_orders, transform_silver_inventory]
    [transform_silver_orders, transform_silver_inventory] >> build_gold_dimensions
    build_gold_dimensions >> build_gold_fact_sales
    build_gold_fact_sales >> validate_data_quality
    validate_data_quality >> refresh_superset_cache
    refresh_superset_cache >> pipeline_completed
