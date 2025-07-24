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
---
## High‑Level Overview

### 1. Ingestion (`ingest/`) 
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

---
## Prerequisites & Configuration

- **Python**: 3.8+  
- **GCP Credentials**: Set up Application Default Credentials for BigQuery & GCS.  
- **MongoDB**: Running locally or via VM; configured in `config/mongo.yaml`.

- **YAML Configs**:
  - `config/gcp.yaml`: GCS bucket, BigQuery dataset, Pub/Sub subscription.  
  - `config/mongo.yaml`: Mongo URI, database, and collection names.  
  - `config/ingest.yaml`: IP2Location DB path, product crawl settings.  

- **IP2Location DB**: Download `IP2LOCATION-LITE-DB11.IPV6.BIN` and set its path in `config/ingest.yaml`.  

---
## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/glamira-batch-pipeline.git
cd glamira-batch-pipeline

# Install Python dependencies
pip install -r requirements.txt

# Install dbt dependencies
cd analytics
pip install -r requirements.txt
```

---
## Running the Pipeline

Follow these steps to execute each stage:

```bash

# 1. Enrich IP geolocation data in MongoDB
python ingest/process_ips.py

# 2. Crawl and save product names
scrapy crawl product_spider

# 3. Export data to GCS
#    (dump MongoDB collections to Google Cloud Storage)
python pipeline/export_gcs.py

# 4. Load data into BigQuery
#    (ingest JSONL from GCS into BigQuery raw tables)
python pipeline/load_to_bigquery.py --mode append

# 5. Switch to analytics then seed and build dbt models
cd analytics
dbt seed --select product_names exchange_rates
dbt run --select stg_* dim_* fact_orders
dbt test
```

---
## Project Structure
```
├── ingest/            # JSON cleanup, IP enrichment, product crawling
├── pipeline/          # GCS export, BigQuery load, Pub/Sub trigger
├── analytics/         # dbt project (seeds, staging, marts)
├── config/            # YAML configs for GCP, Mongo, ingest
├── apps/              # CLI wrappers: run_ingest.py, run_pipeline.py
├── libs/              # Shared helper modules
├── data/              # static data (if any)
├── docs/              # architecture diagrams, slides
└── requirements.txt   # top‑level Python dependencies
```


