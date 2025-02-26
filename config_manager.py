import json
import os

CONFIG_FILE = os.path.expanduser('~/Library/Application Support/DyslexiLess/config.json')

def ensure_config_dir():
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

def config_exists():
    return os.path.exists(CONFIG_FILE)

def save_config(config):
    ensure_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_config():
    if not config_exists():
        return None
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)