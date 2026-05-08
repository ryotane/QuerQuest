"""
Config Loader - Runtime Configuration Management

Project_09: Runtime Hardening
- safe defaults の固定化
- config validation
- graceful fallback
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class RuntimeConfig:
    """Runtime Configuration"""
    runtime_profile: str = "lightweight"
    safety_guard: Dict[str, Any] = field(default_factory=lambda: {
        "max_reasoning_steps": 5,
        "max_hypothesis_repeats": 2,
        "max_same_file_reads": 2,
        "observation_cooldown_ms": 500,
        "debug": False,
    })
    collapse_prevention: Dict[str, Any] = field(default_factory=lambda: {
        "planning_ttl_seconds": 5.0,
        "planning_ttl_steps": 10,
        "max_plan_length": 3,
        "anti_meta_threshold": 2,
        "debug": False,
    })
    memory: Dict[str, Any] = field(default_factory=lambda: {
        "max_items": 500,
        "max_active_memory_bytes": 5_000_000,
        "max_archive_memory_bytes": 20_000_000,
        "max_total_memory_bytes": 30_000_000,
        "compression_trigger_ratio": 0.7,
        "swap_prevention": True,
        "swap_threshold_mb": 100,
    })
    token_budget: Dict[str, Any] = field(default_factory=lambda: {
        "max_context_tokens": 50_000,
        "growth_alert_threshold": 10.0,
        "explosion_threshold": 50.0,
        "compression_priority": "high",
    })
    loop_risk: Dict[str, Any] = field(default_factory=lambda: {
        "high_threshold": 0.5,
        "critical_threshold": 0.8,
        "max_injection_count": 5,
        "max_recursion_depth": 3,
        "max_amplification_count": 2,
    })
    observability: Dict[str, Any] = field(default_factory=lambda: {
        "health_check_interval_seconds": 60,
        "export_json": True,
        "export_path": "logs/health_status.json",
        "swiftbar": False,
        "alert_on_critical": True,
    })
    degradation: Dict[str, Any] = field(default_factory=lambda: {
        "on_memory_pressure": "compress_archive",
        "on_loop_risk_critical": "force_observation",
        "on_token_explosion": "compress_context",
        "on_config_error": "use_defaults",
    })
    lightweight_overrides: Dict[str, Any] = field(default_factory=lambda: {
        "embedding_enabled": False,
        "vector_search_enabled": False,
        "compression_enabled": True,
        "telemetry_enabled": False,
        "background_tasks": False,
        "max_reflection_depth": 1,
    })
    validation: Dict[str, Any] = field(default_factory=lambda: {
        "require_safe_defaults": True,
        "reject_negative_values": True,
        "reject_extreme_values": True,
        "extreme_value_limits": {
            "max_reasoning_steps": 20,
            "min_reasoning_steps": 1,
            "max_plan_length": 10,
            "min_plan_length": 1,
            "max_memory_bytes": 100_000_000,
            "min_memory_bytes": 1_000_000,
        },
    })

    def get(self, key: str, default: Any = None) -> Any:
        """Config値を取得"""
        return getattr(self, key, default)

    def is_lightweight(self) -> bool:
        """Lightweightモードか"""
        return self.runtime_profile == "lightweight"

    def is_safe(self) -> bool:
        """安全設定か"""
        return self.validation.get("require_safe_defaults", True)


class ConfigValidationError(Exception):
    """Config validation error"""
    pass


class ConfigLoader:
    """Runtime Configuration Loader"""

    DEFAULT_CONFIG_PATH = "runtime_config.yaml"
    
    # Safe defaults (yamlが読めない場合のフォールバック)
    SAFE_DEFAULTS = {
        "runtime_profile": "lightweight",
        "safety_guard": {
            "max_reasoning_steps": 5,
            "max_hypothesis_repeats": 2,
            "max_same_file_reads": 2,
        },
        "collapse_prevention": {
            "planning_ttl_seconds": 5.0,
            "max_plan_length": 3,
        },
        "memory": {
            "max_items": 500,
            "swap_prevention": True,
        },
        "token_budget": {
            "max_context_tokens": 50_000,
        },
        "degradation": {
            "on_config_error": "use_defaults",
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config: Optional[RuntimeConfig] = None
        self._validation_errors: list = []

    def load(self) -> RuntimeConfig:
        """Configを読み込み、validation実行"""
        try:
            raw_config = self._load_yaml()
            self._validate(raw_config)
            self._config = self._build_config(raw_config)
        except Exception as e:
            # Fail-safe: safe defaultsを使用
            self._config = self._build_config(self.SAFE_DEFAULTS)
            self._validation_errors.append(f"Config load error: {e}")
        
        return self._config

    def get(self) -> RuntimeConfig:
        """Configを取得 (未読み込み時は自動ロード)"""
        if self._config is None:
            return self.load()
        return self._config

    def _load_yaml(self) -> Dict[str, Any]:
        """YAMLファイルを読み込み"""
        path = Path(self.config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _validate(self, config: Dict[str, Any]) -> None:
        """Config validation"""
        limits = config.get("validation", {}).get("extreme_value_limits", {})
        
        # safety_guard validation
        sg = config.get("safety_guard", {})
        if sg.get("max_reasoning_steps", 0) > limits.get("max_reasoning_steps", 20):
            self._validation_errors.append("max_reasoning_steps too high")
        if sg.get("max_reasoning_steps", 0) < limits.get("min_reasoning_steps", 1):
            self._validation_errors.append("max_reasoning_steps too low")
        
        # memory validation
        mem = config.get("memory", {})
        if mem.get("max_items", 0) > 10_000:
            self._validation_errors.append("max_items too high")
        
        # token_budget validation
        tb = config.get("token_budget", {})
        if tb.get("max_context_tokens", 0) > 100_000:
            self._validation_errors.append("max_context_tokens too high")

    def _build_config(self, raw: Dict[str, Any]) -> RuntimeConfig:
        """Raw configからRuntimeConfigを構築"""
        return RuntimeConfig(
            runtime_profile=raw.get("runtime_profile", "lightweight"),
            safety_guard=raw.get("safety_guard", self.SAFE_DEFAULTS["safety_guard"]),
            collapse_prevention=raw.get("collapse_prevention", self.SAFE_DEFAULTS["collapse_prevention"]),
            memory=raw.get("memory", self.SAFE_DEFAULTS["memory"]),
            token_budget=raw.get("token_budget", {"max_context_tokens": 50_000}),
            loop_risk=raw.get("loop_risk", self.SAFE_DEFAULTS.get("loop_risk", {})),
            observability=raw.get("observability", self.SAFE_DEFAULTS.get("observability", {})),
            degradation=raw.get("degradation", self.SAFE_DEFAULTS.get("degradation", {})),
            lightweight_overrides=raw.get("lightweight_overrides", self.SAFE_DEFAULTS.get("lightweight_overrides", {})),
            validation=raw.get("validation", self.SAFE_DEFAULTS.get("validation", {})),
        )

    @property
    def validation_errors(self) -> list:
        return self._validation_errors


# Singleton instance
_config_instance: Optional[ConfigLoader] = None


def get_config(config_path: Optional[str] = None) -> RuntimeConfig:
    """Get runtime config (singleton)"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    return _config_instance.get()


def reset_config():
    """Reset singleton config (testing)"""
    global _config_instance
    _config_instance = None
