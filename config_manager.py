import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return {"appearance": "dark"}
    return {"appearance": "dark"}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
