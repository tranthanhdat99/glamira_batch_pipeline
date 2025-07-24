import json
import datetime
from pymongo.collection import Collection

def read_state(state_file: str):
    """
    Reads {"last_export_time": ISO8601, "last_count": int}
    Returns (datetime or None, int)
    """
    try:
        with open(state_file) as f:
            data = json.load(f)
        ts = datetime.datetime.fromisoformat(data.get("last_export_time", ""))
        cnt = data.get("last_count", 0)
        return ts, cnt
    except Exception:
        return None, 0

def write_state(state_file: str, export_time: datetime.datetime, count: int):
    """
    Writes the export timestamp and count back to disk.
    """
    with open(state_file, "w") as f:
        json.dump({
            "last_export_time": export_time.isoformat(),
            "last_count": count
        }, f)

def has_data_changed(collection: Collection, state_file: str) -> bool:
    """
    Returns True if either the document count has changed
    or the newest _id.generation_time is newer than last_export_time.
    """
    curr_count = collection.count_documents({})
    last_ts, last_cnt = read_state(state_file)

    if curr_count != last_cnt:
        return True

    latest = collection.find_one(sort=[("_id", -1)])
    if latest and latest["_id"].generation_time and last_ts:
        return latest["_id"].generation_time > last_ts

    return False
