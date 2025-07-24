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
def run_export(args):
    from pipeline.export_gcs.export_to_gcs import export_to_gcs
    export_to_gcs()

def run_fix_option(args):
    from pipeline.export_gcs.fix_option_fields import fix_blob_contents
    from yaml import safe_load
    # Read GCS prefixes from config
    cfg = safe_load(open(os.path.join(REPO_ROOT, "config", "gcp.yaml")))["gcp"]
    fix_blob_contents(
        cfg["bucket_name"],
        cfg["data_export_folder"],
        cfg["data_fixed_folder"]
    )

def run_load_bq(args):
    from pipeline.export_gcs.load_to_bigquery import load_files_to_bigquery
    load_files_to_bigquery(mode=args.mode)

def run_full(args):
    # Full pipeline: export → fix_option (optional) → load to BQ
    run_export(args)
    if args.fix:
        run_fix_option(args)
    run_load_bq(args)

# CLI Setup
def main():
    parser = argparse.ArgumentParser(
        description="Run batch pipeline tasks: export → (fix) → load to BigQuery"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    exp = sub.add_parser("export_gcs", help="Export data from MongoDB to GCS")
    exp.set_defaults(func=run_export)

    fix = sub.add_parser("fix_option_fields", help="Clean option fields in exported files")
    fix.set_defaults(func=run_fix_option)

    bq = sub.add_parser("load_to_bq", help="Load JSONL files from GCS to BigQuery")
    bq.add_argument(
        "--mode", choices=["append", "replace"],
        default="append", help="BigQuery write mode"
    )
    bq.set_defaults(func=run_load_bq)

    full = sub.add_parser("full_pipeline", help="Run export, fix, then load to BigQuery")
    full.add_argument(
        "--fix", action="store_true",
        help="Run the option‑field fix step between export and load"
    )
    full.add_argument(
        "--mode", choices=["append", "replace"],
        default="append",
        help="BigQuery write mode for the load step"
    )
    full.set_defaults(func=run_full)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception:
        logger.exception("Pipeline command `%s` failed", args.command)
        sys.exit(1)

if __name__ == "__main__":
    main()
