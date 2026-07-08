# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fastapi>=0.139.0",
#     "python-dotenv>=1.2.2",
#     "pyyaml>=6.0.3",
#     "uvicorn>=0.51.0",
# ]
# ///

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import yaml
import os

# -----------------------------
# Load .env into environment
# -----------------------------
load_dotenv()

app = FastAPI()

# -----------------------------
# Enable CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Default configuration
# -----------------------------
defaults = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


# -----------------------------
# Convert values to correct types
# -----------------------------
def convert_type(key, value):
    if key in ["port", "workers"]:
        return int(value)

    if key == "debug":
        return str(value).lower() in ["true", "1", "yes", "on"]

    return str(value)


# -----------------------------
# Read YAML
# -----------------------------
def load_yaml():
    filename = "config.development.yaml"

    if not os.path.exists(filename):
        return {}

    with open(filename, "r") as f:
        return yaml.safe_load(f) or {}


# -----------------------------
# Read .env values
# -----------------------------
def load_dotenv_config():
    config = {}

    mapping = {
        "APP_PORT": "port",
        "APP_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
    }

    for env_key, config_key in mapping.items():
        value = os.getenv(env_key)

        if value is not None:
            config[config_key] = convert_type(config_key, value)

    # Alias
    num_workers = os.getenv("NUM_WORKERS")
    if num_workers is not None:
        config["workers"] = int(num_workers)

    return config


# -----------------------------
# Read ONLY OS APP_* variables
# (Higher precedence than .env)
# -----------------------------
def load_os_env():

    config = {}

    mapping = {
        "APP_PORT": "port",
        "APP_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
    }

    for env_key, config_key in mapping.items():

        if env_key in os.environ:

            value = os.environ[env_key]
            config[config_key] = convert_type(config_key, value)

    return config


# -----------------------------
# Endpoint
# -----------------------------
@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):

    config = defaults.copy()

    # YAML
    config.update(load_yaml())

    # .env
    config.update(load_dotenv_config())

    # OS env
    config.update(load_os_env())

    # CLI overrides
    for item in set:

        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        config[key] = convert_type(key, value)

    # Mask secret
    config["api_key"] = "****"

    return config