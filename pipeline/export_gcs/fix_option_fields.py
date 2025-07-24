import json, logging, yaml
from google.cloud import storage

cfg = yaml.safe_load(open("config/gcp.yaml"))
log_cfg = "config/logging.yaml"
logging.config.fileConfig(log_cfg)
logger = logging.getLogger(__name__)

def fix_blob_contents(bucket, src_prefix, dst_prefix):
    client = storage.Client()
    for blob in client.list_blobs(bucket, prefix=src_prefix):
        if not blob.name.endswith(".jsonl"): continue
        data = blob.download_as_text().splitlines()
        fixed = []
        for line in data:
            doc = json.loads(line)
            # <same option‑fixing logic as before>
            fixed.append(json.dumps(doc))
        out = "\n".join(fixed)
        client.bucket(bucket).blob(blob.name.replace(src_prefix, dst_prefix)).upload_from_string(out)
        logger.info(f"Fixed {blob.name}")

if __name__=="__main__":
    fix_blob_contents(cfg["gcp"]["bucket_name"],
                      cfg["gcp"]["data_export_folder"],
                      cfg["gcp"]["data_fixed_folder"])
