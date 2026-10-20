import yaml
import os


def test_config():
    config_path = os.path.join("config", "settings.yaml")
    assert os.path.exists(config_path), "settings.yaml missing!"

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    assert "paths" in config, "Missing 'paths' section in settings"
    assert "databases" in config, "Missing 'databases' section in settings"
    print("[SUCCESS] Configuration file loaded and validated successfully.")


if __name__ == "__main__":
    test_config()
