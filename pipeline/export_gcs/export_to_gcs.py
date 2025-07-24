import json
import logging
import datetime
import yaml
from pymongo import MongoClient
from google.cloud import storage
from libs.mongo_utils import read_state, write_state, has_data_changed

# Load configs
cfg = yaml.safe_load(open("config/gcp.yaml"))["gcp"]
mongo_cfg = yaml.safe_load(open("config/mongo.yaml"))["mongo"]
log_cfg = "config/logging.yaml"

import logging.config
logging.config.fileConfig(log_cfg)
logger = logging.getLogger(__name__)

# Config‑driven values
STATE_FILE = cfg["state_file"]
BATCH_SIZE = cfg["batch_size"]
# Collections to export: summary and IP geolocation
COLLECTIONS_TO_EXPORT = [
    mongo_cfg["collections"]["summary"],
    mongo_cfg["collections"]["ip_locations"]
]


def export_collection(collection_name):
    """
    Exports a single MongoDB collection to GCS JSONL files under a folder named after the collection.
    """
    client = MongoClient(mongo_cfg["uri"])
    db = client[mongo_cfg["database"]]
    col = db[collection_name]
    storage_client = storage.Client()
    bucket = storage_client.bucket(cfg["bucket_name"])

    # Use separate state file per collection
    state_file = f"{collection_name}_{STATE_FILE}"
    if not has_data_changed(col, state_file):
        logger.info("No new data in '%s'; skipping export.", collection_name)
        client.close()
        return

    total = col.count_documents({})
    logger.info("Exporting %s: %d documents in batches to GCS", collection_name, total)

    cursor = col.find({}, no_cursor_timeout=True)
    batch = []
    batch_number = 1

    for idx, doc in enumerate(cursor, start=1):
        batch.append(doc)
        if idx % BATCH_SIZE == 0 or idx == total:
            filename = f"{cfg['data_export_folder']}/{collection_name}/batch_{batch_number}.jsonl"
            content = "\n".join(json.dumps(d, default=str) for d in batch)
            bucket.blob(filename).upload_from_string(content, content_type="application/json")
            logger.info("Uploaded %s (%d docs)", filename, len(batch))
            batch.clear()
            batch_number += 1

    cursor.close()
    write_state(state_file, datetime.datetime.utcnow(), total)
    client.close()
    logger.info("Export job for '%s' complete.", collection_name)


def export_to_gcs():
    for coll in COLLECTIONS_TO_EXPORT:
        export_collection(coll)


if __name__ == "__main__":
    export_to_gcs()

