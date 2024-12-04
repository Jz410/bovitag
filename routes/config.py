import json
import os

CONFIG_FILE = 'config.json'

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'output_folder': '',
            'output_size_width': 497,
            'output_size_height': 535
        }
