import json
import mlflow
import tempfile
import os
import wandb
import hydra
import yaml
import importlib
from omegaconf import DictConfig
from omegaconf import OmegaConf
import pandas as pd
import subprocess

_steps = ["download", "data_check", "data_split", "train_random_forest"]
    # NOTE: We do not include this in the steps so it is not run by mistake.
    # You first need to promote a model export to "prod" before you can run this,
    # then you need to run this step explicitly
#    "test_regression_model"

# This automatically reads in the configuration
@hydra.main(config_path=".", config_name="config", version_base=None)
def go(config: DictConfig):
    print("✅ Go function is being called")
    print("🧾 Config contents:")
    print(OmegaConf.to_yaml(config))

  # Initialize wandb before starting
    wandb.init(project=config['main']['project_name'], name=config['main']['experiment_name'])
    
    # Setup the wandb experiment. All runs will be grouped under this name
    os.environ["WANDB_PROJECT"] = config["main"]["project_name"]
    os.environ["WANDB_RUN_GROUP"] = config["main"]["experiment_name"]

    # Steps to execute
    steps_par = config['main']['steps']
    active_steps = [step.strip() for step in steps_par.split(",")] if steps_par != "all" else _steps

    # Print active steps inside the function
    print("🔍 Active steps parsed as:", active_steps)

    # Move to a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        if "download" in active_steps:
            print("Downloading data...")
            # Download file and load in W&B
            _ = mlflow.run(
                f"{config['main']['components_repository']}/get_data", "main",
                version='main',
                env_manager="conda",
                parameters={
                    "sample": config["etl"]["sample"],
                    "artifact_name": "sample.csv",
                    "artifact_type": "raw_data",
                    "artifact_description": "Raw file as downloaded"
                },
            )
            print("Data download complete.")

        if "basic_cleaning" in active_steps:
            print("Completing basic cleaning")
            _ = mlflow.run(
            os.path.join(config["main"]["components_repository"], "basic_cleaning"), "main",
            parameters={
                "input_artifact": config["basic_cleaning"]["input_artifact"],
                "output_artifact": config["basic_cleaning"]["output_artifact"],
                "output_type": config["basic_cleaning"]["output_type"],
                "output_description": config["basic_cleaning"]["output_description"],
                "min_price": config["basic_cleaning"]["min_price"],
                "max_price": config["basic_cleaning"]["max_price"],
            },
        )
        print("basic cleaning complete")

        if "data_check" in active_steps:
            print("Running data checks...")
            # Load the data artifact from W&B
            artifact = wandb.Api().artifact(config["basic_cleaning"]["output_artifact"], type="cleaned_data")
            artifact.download(root=tmp_dir)
            
            # Load the cleaned sample data into a pandas DataFrame
            cleaned_data_path = os.path.join(tmp_dir, "clean_sample.csv")
            data = pd.read_csv(cleaned_data_path)

            # Now we will import the test functions dynamically
            test_module = importlib.import_module('src.data_check.test_data')

            # Run the data check tests
            test_module.test_column_names(data)
            test_module.test_neighborhood_names(data)
            test_module.test_proper_boundaries(data)
            test_module.test_row_count(data)
            test_module.test_price_range(data, config["basic_cleaning"]["min_price"], config["basic_cleaning"]["max_price"])

            print("Data checks complete.")

        if "data_split" in active_steps:
            print("Running data_split...")
            _ = mlflow.run(
                f"{config['main']['components_repository']}/train_val_test_split", 'main',
                parameters ={
                    "input": "clean_sample.csv:latest",
                    "test_size": config['modeling']['test_size'],
                    "random_seed": config['modeling']['random_seed'],
                    "stratify_by": config['modeling']['stratify_by']
                }
            )

        if "train_random_forest" in active_steps:

            # NOTE: we need to serialize the random forest configuration into JSON
            rf_config = os.path.abspath("rf_config.json")
            with open(rf_config, "w+") as fp:
                json.dump(dict(config["modeling"]["random_forest"].items()), fp)  # DO NOT TOUCH

            # NOTE: use the rf_config we just created as the rf_config parameter for the train_random_forest
            # step

            ##################
            # Implement here #
            ##################

            subprocess.run([
                "mlflow", "run", 
                os.path.join("src", "train_random_forest"), 
                "-P", f"trainval_artifact=trainval_data.csv:latest",
                "-P", f"rf_config={rf_config}",
                "-P", "output_artifact=random_forest_export"
            ], check=True)

        if "test_regression_model" in active_steps:

            ##################
            # Implement here #
            ##################

            pass

if __name__ == "__main__":
    go()