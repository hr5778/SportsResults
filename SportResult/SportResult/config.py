import json


def api_setting():
    with open(r'SportResult\config.json') as f:
        config = json.load(f)
    return config
