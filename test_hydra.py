import hydra
from omegaconf import DictConfig

@hydra.main(config_path=".", config_name="config")
def test_hydra(config: DictConfig):
    print(config)

if __name__ == "__main__":
    test_hydra()
