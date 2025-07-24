# Glamira Batch Data Pipeline & Analytics

A streamlined batch ETL and analytics workflow for the Glamira clickstream dataset (same source as the streaming pipeline project), transforming raw JSONL events into a star‑schema in BigQuery with dbt.

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
