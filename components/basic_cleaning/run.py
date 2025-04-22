#!/usr/bin/env python
"""
Basic cleaning step for price outliers and logging cleaned artifact.
"""

import argparse
import pandas as pd
import wandb
import os

def go(args):
    run = wandb.init(job_type="basic_cleaning")
    run.config.update(vars(args))

    # Download input artifact from W&B
    artifact = run.use_artifact(args.input_artifact)
    df = pd.read_csv(artifact.file())

    # Clean: remove outliers
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    # Save cleaned data
    os.makedirs("cleaned_data", exist_ok=True)
    cleaned_path = os.path.join("cleaned_data", "clean_sample.csv")
    df.to_csv(cleaned_path, index=False)

    # Log the cleaned artifact to W&B
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(cleaned_path)
    run.log_artifact(artifact)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean data")

    parser.add_argument("input_artifact", type=str, required=True, help="Raw dataset artifact from W&B")
    parser.add_argument("output_artifact", type=str, required= True, help="Name for the cleaned data artifact")
    parser.add_argument("output_type", type=str, required= True, help="Artifact type")
    parser.add_argument("output_description", type=str, required= True, help="Artifact description")
    parser.add_argument("min_price", type=float, required= True, help="Minimum price to keep")
    parser.add_argument("max_price", type=float, required= True, help="Maximum price to keep")

    args = parser.parse_args()

    go(args)
