#!/usr/bin/env python3
import os
import sys
import argparse
import logging
import logging.config

# Ensure repo root is on pythonpath
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

# Configure logging
logging.config.fileConfig(os.path.join(REPO_ROOT, "config", "logging.yaml"))
logger = logging.getLogger(__name__)

# Task Runners
def run_ip_geolocation(args):
    from ingest.ip_geolocation.process_ips import enrich_and_store
    enrich_and_store(use_cache=not args.no_cache)

def run_product_names(args):
    from ingest.product_names.extract_names import extract_product_names
    extract_product_names()

# CLI Setup
def main():
    parser = argparse.ArgumentParser(
        description="Run ingest tasks for the Glamira pipeline"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ip = sub.add_parser("ip_geolocation", help="Enrich IPs and store locations")
    ip.add_argument(
        "--no-cache", action="store_true",
        help="Ignore cached IP or location files and re-query everything"
    )
    ip.set_defaults(func=run_ip_geolocation)

    pn = sub.add_parser("product_names", help="Extract product names to CSV")
    pn.set_defaults(func=run_product_names)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        logger.exception("Task `%s` failed", args.command)
        sys.exit(1)

if __name__ == "__main__":
    main()
