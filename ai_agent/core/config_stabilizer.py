"""
config_stabilizer.py - 設定固定化 + 変更検知

Project_09: Runtime Hardening
「安定性の固定化」

設定ファイルの変更を検知し、
予期せぬ設定変更からランタイムを保護する。
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ConfigStabilizer:
    """設定固定化 + 変更検知"""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.current_hash: Optional[str] = None
        self.config_changed: bool = False
        self._load_hash()

    def _load_hash(self):
        """現在の設定ファイルのハッシュをロード"""
        if self.config_path.exists():
            content = self.config_path.read_text(encoding="utf-8")
            self.current_hash = hashlib.sha256(content.encode()).hexdigest()
        else:
            self.current_hash = None

    def check_changes(self) -> bool:
        """設定変更を検知"""
        if not self.config_path.exists():
            return False

        content = self.config_path.read_text(encoding="utf-8")
        new_hash = hashlib.sha256(content.encode()).hexdigest()

        if self.current_hash and new_hash != self.current_hash:
            self.config_changed = True
            logger.warning(f"[config_stabilizer] Config changed: {self.config_path}")
            self.current_hash = new_hash
            return True

        self.config_changed = False
        return False

    def get_config(self) -> Optional[Dict[str, Any]]:
        """設定ファイルを読み込み"""
        if not self.config_path.exists():
            return None

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"[config_stabilizer] Failed to load config: {e}")
            return None

    def is_stable(self) -> bool:
        """設定が安定しているか"""
        return not self.config_changed

    def reset_change_flag(self):
        """変更フラグをリセット"""
        self.config_changed = False


# グローバルインスタンス (初期化時は None)
config_stabilizer: Optional[ConfigStabilizer] = None


def init_config_stabilizer(config_path: str) -> ConfigStabilizer:
    """ConfigStabilizer を初期化"""
    global config_stabilizer
    config_stabilizer = ConfigStabilizer(config_path)
    return config_stabilizer
