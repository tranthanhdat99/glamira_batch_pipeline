# Glamira Batch Data Pipeline & Analytics

A streamlined batch ETL and analytics workflow for the Glamira clickstream dataset, transforming raw JSONL events into a star‑schema in BigQuery with dbt.

---

## Pipeline Architecture Diagram

```text
[ MongoDB (summary & ip_locations) ]
               │
               ▼
       [ Export data to GCS ]
               │
               ▼
[ Google Cloud Storage (JSONL files) ]
               │
               ▼
 [ Load data into BigQuery ]
               │
               ▼
  [ BigQuery raw tables ]
               │
               ▼
        [ dbt staging ]
               │
               ▼
        [ dbt marts ]
               │
               ▼
 [ Analytics-ready star schema ]
```
## High‑Level Overview

### 1. Ingestion & Cleanup (`ingest/`)
- **`correct_database.py`**: Normalize malformed JSONL in GCS.  
- **`process_ips.py`**: Lookup and store IP geolocation (country, region, city).  
- **`product_crawler/`**: Scrapy spider to crawl and save product names.  

### 2. Batch Pipeline (`pipeline/`)
- **`export_gcs.py`**: Dump MongoDB collections (`summary`, `ip_locations`) as JSONL to GCS.  
- **`load_to_bigquery.py`**: Ingest JSONL from GCS into BigQuery raw tables.  
- **`trigger_bq_load.py`**: Pub/Sub listener to automate exports on demand.  

### 3. Analytics Models (`analytics/`)
- **Seeds**: `product_names.csv`, `exchange_rates.csv`.  
- **Staging** (`stg_*`): Clean and shape raw BigQuery tables into staging views.  
- **Marts** (`dim_*`, `fact_orders`): Build canonical dimension tables and the `fact_orders` fact in a star schema.  

