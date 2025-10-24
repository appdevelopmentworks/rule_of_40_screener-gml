"""
設定ファイル読み込み
"""

import logging
from pathlib import Path
from typing import Any, Dict

import yaml

try:
    from ..domain.models import ConfigError
except ImportError:
    from src.core.domain.models import ConfigError


logger = logging.getLogger(__name__)


class ConfigManager:
    """設定管理クラス"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """設定ファイルを読み込み"""
        try:
            if self.config_path.exists():
                with open(self.config_path, encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or {}
                logger.info(f"Loaded config from {self.config_path}")
            else:
                logger.warning(
                    f"Config file not found: {self.config_path}, using defaults"
                )
                self._config = {}

        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to load config file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得（ドット区切り対応: ui.theme）"""
        try:
            keys = key.split(".")
            value = self._config

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default

            return value

        except Exception as e:
            logger.warning(f"Error getting config key '{key}': {e}")
            return default

    def set(self, key: str, value: Any):
        """設定値を設定"""
        try:
            keys = key.split(".")
            config = self._config

            # 階層を辿って設定
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            config[keys[-1]] = value
            logger.debug(f"Set config key '{key}' to {value}")

        except Exception as e:
            logger.warning(f"Error setting config key '{key}': {e}")

    def save(self):
        """設定をファイルに保存"""
        try:
            # ディレクトリ作成
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"Saved config to {self.config_path}")

        except Exception as e:
            raise ConfigError(f"Failed to save config file: {e}")

    def reload(self):
        """設定を再読み込み"""
        self._load_config()

    def get_all(self) -> Dict[str, Any]:
        """全設定を取得"""
        return self._config.copy()

    def update(self, updates: Dict[str, Any]):
        """設定を一括更新"""
        try:
            for key, value in updates.items():
                self.set(key, value)
            logger.info(f"Updated config with {len(updates)} keys")
        except Exception as e:
            logger.warning(f"Error updating config: {e}")

    def validate(self) -> bool:
        """設定のバリデーション"""
        try:
            # 必須キーのチェック
            required_keys = [
                "ui.theme",
                "fetch.max_workers",
                "rule40.threshold",
                "cache.enabled",
            ]

            for key in required_keys:
                if self.get(key) is None:
                    logger.warning(f"Missing required config key: {key}")
                    return False

            # 値の範囲チェック
            max_workers = self.get("fetch.max_workers", 0)
            if not isinstance(max_workers, int) or max_workers < 1 or max_workers > 50:
                logger.warning(f"Invalid fetch.max_workers: {max_workers}")
                return False

            threshold = self.get("rule40.threshold", 0)
            if not isinstance(threshold, (int, float)) or threshold < 0:
                logger.warning(f"Invalid rule40.threshold: {threshold}")
                return False

            return True

        except Exception as e:
            logger.warning(f"Config validation error: {e}")
            return False
