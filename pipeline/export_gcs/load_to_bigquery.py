import logging
import logging.config
import yaml
from google.cloud import bigquery

# Setup Logging & Config
logging.config.fileConfig("config/logging.yaml")
logger = logging.getLogger(__name__)

# Load GCP config
gcp_cfg = yaml.safe_load(open("config/gcp.yaml"))["gcp"]

# Core settings
BQ_DATASET  = gcp_cfg["bigquery_dataset"]
BUCKET      = gcp_cfg["bucket_name"]
SRC_FOLDER  = gcp_cfg["data_export_folder"]
BQ_TABLES   = gcp_cfg["bigquery_tables"]

def load_schema(schema_path):
    """Load a JSON schema file and return its dict representation."""
    import json
    with open(schema_path) as f:
        return json.load(f)

def load_files_to_bigquery(mode="append"):
    """
    Load JSONL files from GCS into BigQuery tables as defined in BQ_TABLES.
    mode: "append" or "replace"
    """
    client = bigquery.Client()
    dataset_ref = client.dataset(BQ_DATASET)

    for prefix, props in BQ_TABLES.items():
        table_name  = props["table"]
        schema_path = props.get("schema")

        table_ref = dataset_ref.table(table_name)
        prefix_path = f"{SRC_FOLDER}/{prefix}/"

        # List all .jsonl files under this GCS prefix
        uris = [
            f"gs://{BUCKET}/{blob.name}"
            for blob in client.list_blobs(BUCKET, prefix=prefix_path)
            if blob.name.endswith(".jsonl")
        ]

        if not uris:
            logger.warning("No files found in GCS folder '%s'", prefix_path)
            continue

        # Configure load job
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=(
                bigquery.WriteDisposition.WRITE_TRUNCATE if mode == "replace"
                else bigquery.WriteDisposition.WRITE_APPEND
            )
        )

        if schema_path:
            # Use provided JSON schema
            schema_fields = [bigquery.SchemaField(**fld) for fld in load_schema(schema_path)]
            job_config.schema = schema_fields
        else:
            # Let BigQuery autodetect schema
            job_config.autodetect = True

        # Execute load for each file
        for uri in uris:
            logger.info("Loading %s → %s.%s (%s)", uri, BQ_DATASET, table_name, mode)
            load_job = client.load_table_from_uri(uri, table_ref, job_config=job_config)
            try:
                load_job.result()
                logger.info("Loaded %d rows from %s", load_job.output_rows, uri)
            except Exception as e:
                logger.error("Failed to load %s: %s", uri, e)

    logger.info("BigQuery load process completed.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Load GCS JSONL files to BigQuery")
    parser.add_argument(
        "--mode",
        choices=["append", "replace"],
        default="append",
        help="Write mode for BigQuery load: append or replace"
    )
    args = parser.parse_args()
    load_files_to_bigquery(mode=args.mode)
