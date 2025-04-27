import wandb

run = wandb.init(project="Project-Build-an-ML-Pipeline-Starter-components_basic_cleaning", job_type="upload_file")

artifact = wandb.Artifact(
    name="sample.csv",
    type="raw_data",
    description="Initial dataset uploaded manually"
)
artifact.add_file("sample.csv")  # Make sure sample.csv exists in your project root or provide full path

run.log_artifact(artifact)
run.finish()