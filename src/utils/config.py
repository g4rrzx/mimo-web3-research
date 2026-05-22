"""Config loader — combines .env + config.yaml."""
import os
from pathlib import Path
from typing import Any
import yaml
from dotenv import load_dotenv


class Config:
    """Unified config access for env vars + YAML."""

    def __init__(self, config_path: str = "config.yaml", env_path: str = ".env"):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.config_path = self.root / config_path
        self.env_path = self.root / env_path

        # Load .env
        if self.env_path.exists():
            load_dotenv(self.env_path)

        # Load YAML config
        self._yaml = {}
        if self.config_path.exists():
            with open(self.config_path) as f:
                self._yaml = yaml.safe_load(f) or {}

    def env(self, key: str, default: Any = None) -> str:
        """Get environment variable."""
        return os.getenv(key, default)

    def get(self, path: str, default: Any = None) -> Any:
        """Get YAML config value via dot notation (e.g., 'whale_watching.enabled')."""
        keys = path.split(".")
        value = self._yaml
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def require_env(self, key: str) -> str:
        """Get env var or raise if missing."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value


# Singleton
_config = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config
