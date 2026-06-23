import os
import json

env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
config_path = os.path.join(os.path.dirname(__file__), 'config.json')

env_vars = {}
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                env_vars[k] = v

if os.path.exists(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
else:
    config = {"language": "en", "host": "127.0.0.1", "port": 3000}

if 'USERNAME' in env_vars:
    config['username'] = env_vars['USERNAME']
if 'PASSWORD' in env_vars:
    config['password'] = env_vars['PASSWORD']

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)
