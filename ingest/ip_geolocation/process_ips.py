import os
import json
import logging
import yaml
from pymongo import MongoClient
import IP2Location

# Load configs & logging
cfg_all = yaml.safe_load(open("config/ingest.yaml"))["ingest"]
mongo_cfg = yaml.safe_load(open("config/mongo.yaml"))["mongo"]
log_cfg  = "config/logging.yaml"

import logging.config
logging.config.fileConfig(log_cfg)
logger = logging.getLogger(__name__)

# MongoDB setup
client      = MongoClient(mongo_cfg["uri"])
db          = client[mongo_cfg["database"]]
summary_col = db[mongo_cfg["collections"]["summary"]]
ip_col      = db[mongo_cfg["collections"]["ip_locations"]]

# IP2Location DB
db_path = cfg_all.get("ip2location_db_path")
if not db_path or not os.path.isfile(db_path):
    logger.error(f"IP2Location DB not found at '{db_path}'. Exiting.")
    raise FileNotFoundError(f"IP2Location DB not found at '{db_path}'")
ip2loc = IP2Location.IP2Location(db_path)

# Helpers
def get_unique_ips(cache=True):
    cache_file = cfg_all["cache_file_ips"]
    if cache and os.path.exists(cache_file):
        logger.info(f"Loading cached IPs from {cache_file}")
        return json.load(open(cache_file))

    logger.info("Querying MongoDB for unique IPs...")
    pipeline = [{"$group": {"_id": "$ip"}}]
    ips = [d["_id"] for d in summary_col.aggregate(pipeline)]
    json.dump(ips, open(cache_file, "w"), indent=2)
    logger.info(f"Discovered {len(ips)} unique IPs")
    return ips

# Main enrichment
def enrich_and_store(use_cache=True):
    # load or compute locations
    loc_cache = cfg_all["cache_file_loc"]
    if use_cache and os.path.exists(loc_cache):
        logger.info(f"Loading cached locations from {loc_cache}")
        locations = json.load(open(loc_cache))
    else:
        ips = get_unique_ips(cache=use_cache)
        locations = []
        for ip in ips:
            try:
                rec = ip2loc.get_all(ip)
                locations.append({
                    "ip":       ip,
                    "country_short":  rec.country_short,
                    "country_long":  rec.country_long,
                    "region":   rec.region,
                    "city":     rec.city,
                    "timezone": rec.timezone
                })
            except Exception as e:
                logger.warning(f"[{ip}] lookup failed: {e}")
        json.dump(locations, open(loc_cache, "w"), indent=2)
        logger.info(f"Enriched {len(locations)} IPs")

    # upsert into MongoDB
    for loc in locations:
        ip_col.update_one({"ip": loc["ip"]}, {"$set": loc}, upsert=True)
    logger.info("All IP locations written to MongoDB")
    client.close()
    return locations

if __name__ == "__main__":
    enrich_and_store(use_cache=True)
