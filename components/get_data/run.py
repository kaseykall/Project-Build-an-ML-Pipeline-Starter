#!/usr/bin/env python
"""
This script uploads a sample file as an artifact to Weights & Biases (W&B).
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import logging
import wandb
import pandas as pd
from wandb_utils.log_artifact import log_artifact

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):
    """
    Uploads a sample file to W&B as an artifact.
    Args:
        args (argparse.Namespace): Parsed command-line arguments containing:
            - sample (str): Name of the sample file in the 'data/' folder to upload.
            - artifact_name (str): Name for the output artifact in W&B.
            - artifact_type (str): Type/category of the artifact (e.g., 'dataset').
            - artifact_description (str): A brief description of the artifact.
    """

    run = wandb.init(job_type="get_data")
    run.config.update({"input_path": "sample1.csv"})  # Convert Namespace to dict before logging

    logger.info(f"Returning sample {args.sample}")
    logger.info(f"Uploading artifact '{args.artifact_name}' to Weights & Biases")
    
    # Compute the full path to the data file
    sample_path = os.path.join(os.path.dirname(__file__), "data", args.sample)

    log_artifact(
        args.artifact_name,
        args.artifact_type,
        args.artifact_description,
        sample_path,
        run,
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a sample file to W&B.")

    parser.add_argument("sample", type=str, help="Name of the sample to download")

    parser.add_argument("artifact_name", type=str, help="Name for the output artifact")

    parser.add_argument("artifact_type", type=str, help="Output artifact type.")

    parser.add_argument(
        "artifact_description", type=str, help="A brief description of this artifact"
    )

    args = parser.parse_args()

    go(args)
