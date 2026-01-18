import os
import typer
from pathlib import Path
from dotenv import load_dotenv, set_key

APP_NAME = "gemini-cli"
CONFIG_DIR = typer.get_app_dir(APP_NAME)
CONFIG_PATH = Path(CONFIG_DIR) / "config.env"

def get_api_key():
    """Retrieves the API key from environment variables or the config file."""
    # 1. Check environment variable (highest priority)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key

    # 2. Check config file
    if CONFIG_PATH.exists():
        load_dotenv(CONFIG_PATH)
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            return api_key
    
    return None

def set_api_key(api_key: str):
    """Saves the API key to the config file."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    
    # Touch file if it doesn't exist
    if not CONFIG_PATH.exists():
         with open(CONFIG_PATH, 'w') as f:
            pass

    set_key(CONFIG_PATH, "GEMINI_API_KEY", api_key)
    typer.echo(f"API key saved to {CONFIG_PATH}")
