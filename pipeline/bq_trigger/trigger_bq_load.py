import os
import sys
import json
import subprocess
import logging
import logging.config
import yaml
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.message import Message

# Helpers
def load_config():
    with open(os.path.join("config", "gcp.yaml"), "r") as f:
        return yaml.safe_load(f)["gcp"]

def setup_logging():
    logging.config.fileConfig(os.path.join("config", "logging.yaml"))

# Callback
def callback(message: Message) -> None:
    """Handle incoming Pub/Sub message, triggering the export pipeline."""
    try:
        payload = message.data.decode("utf-8")
        data = json.loads(payload)
    except Exception:
        logger.exception("Invalid message received, nacking")
        message.nack()
        return

    action = data.get("action")
    if action == "start_export":
        cmd = [
            sys.executable,
            os.path.join("apps", "run_pipeline.py"),
            "export_gcs"
        ]
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            logger.info("Export script succeeded: %s", result.stdout.strip())
        except subprocess.CalledProcessError as e:
            logger.error("Export script failed: %s", e.stderr.strip())
    else:
        logger.warning("Received unsupported action: %r", action)

    message.ack()

# Main Entrypoint
def main():
    cfg = load_config()
    setup_logging()
    global logger
    logger = logging.getLogger(__name__)

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        cfg["project_id"],
        cfg["pubsub_subscription"]
    )
    logger.info("Listening for Pub/Sub messages on %s", subscription_path)

    streaming_pull = subscriber.subscribe(subscription_path, callback=callback)
    try:
        streaming_pull.result()
    except KeyboardInterrupt:
        logger.info("Shutdown requested; cancelling subscriber...")
        streaming_pull.cancel()

if __name__ == "__main__":
    main()
