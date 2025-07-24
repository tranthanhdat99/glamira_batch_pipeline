import os
import json
import yaml
import logging
import logging.config
from google.cloud import bigquery

def load_config():
    with open(os.path.join("config", "gcp.yaml"), "r") as f:
        return yaml.safe_load(f)["gcp"]

def setup_logging():
    logging.config.fileConfig(os.path.join("config", "logging.yaml"))

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    cfg = load_config()

    client = bigquery.Client(project=cfg["project_id"])

    # Dataset setup
    dataset_id = cfg["bigquery_dataset"]
    dataset_ref = bigquery.DatasetReference(cfg["project_id"], dataset_id)
    dataset = bigquery.Dataset(dataset_ref)

    try:
        client.create_dataset(dataset, exists_ok=True)
        logger.info(f"Dataset `{dataset_id}` is ready")
    except Exception as e:
        logger.error(f"Failed to create dataset `{dataset_id}`: {e}")
        raise

    # Table setup
    table_id = cfg["bigquery_table"]
    table_ref = dataset_ref.table(table_id)

    # Load schema from JSON file
    schema_path = cfg["bigquery_schema"]
    with open(schema_path) as f:
        schema_json = json.load(f)
    schema = [bigquery.SchemaField(**field) for field in schema_json]

    table = bigquery.Table(table_ref, schema=schema)
    try:
        client.create_table(table, exists_ok=True)
        logger.info(f"Table `{dataset_id}.{table_id}` is ready")
    except Exception as e:
        logger.error(f"Failed to create table `{dataset_id}.{table_id}`: {e}")
        raise

if __name__ == "__main__":
    main()
