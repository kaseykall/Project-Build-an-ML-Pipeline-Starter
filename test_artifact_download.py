import wandb

wandb.init(project="nyc_airbnb", entity="kasey-kallevig-western-governors-university")

artifact = wandb.use_artifact('raw_data:latest')
artifact_dir = artifact.download()
print(f"Artifact downloaded to: {artifact_dir}")

