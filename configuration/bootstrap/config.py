# src/config.py

from pathlib import Path
import os

import yaml
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

# 全域配置
_CONFIG = {}

# 掃描 config/*.yaml
config_dir = Path(__file__).parent.parent / "config"

for file in config_dir.glob("*.yaml"):
    namespace = file.stem

    with open(file, "r", encoding="utf-8") as f:
        _CONFIG[namespace] = yaml.safe_load(f) or {}


def config(key: str, default=None):
    """
    config("grpc.port")
    config("redis.host")
    """

    # grpc.port -> GRPC_PORT
    env_key = key.upper().replace(".", "_")

    if env_key in os.environ:
        return os.environ[env_key]

    try:
        value = _CONFIG

        for part in key.split("."):
            value = value[part]

        return value

    except (KeyError, TypeError):
        return default


def all_config():
    return _CONFIG