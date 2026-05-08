"""
runtime_profile.py - Runtime Profile 定義

Project_09: Runtime Hardening
「安定性の固定化」

lightweight / balanced / full の3モードを定義。
デフォルトは lightweight。
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class ProfileConfig:
    """単一プロファイルの設定"""
    max_tokens: int
    temperature: float
    max_plan_steps: int
    plan_timeout: int
    max_reflections: int
    reflection_timeout: int
    max_memory_mb: int
    max_memory_entries: int
    max_context_tokens: int
    swap_threshold_mb: int
    description: str


# プロファイル定義
PROFILES: Dict[str, ProfileConfig] = {
    "lightweight": ProfileConfig(
        max_tokens=1024,
        temperature=0.3,
        max_plan_steps=3,
        plan_timeout=30,
        max_reflections=1,
        reflection_timeout=15,
        max_memory_mb=512,
        max_memory_entries=256,
        max_context_tokens=50_000,
        swap_threshold_mb=100,
        description="Mac-friendly. Low CPU, low memory, low swap.",
    ),
    "balanced": ProfileConfig(
        max_tokens=2048,
        temperature=0.5,
        max_plan_steps=5,
        plan_timeout=60,
        max_reflections=2,
        reflection_timeout=30,
        max_memory_mb=1024,
        max_memory_entries=512,
        max_context_tokens=100_000,
        swap_threshold_mb=500,
        description="Balanced performance and resource usage.",
    ),
    "full": ProfileConfig(
        max_tokens=4096,
        temperature=0.7,
        max_plan_steps=10,
        plan_timeout=120,
        max_reflections=3,
        reflection_timeout=60,
        max_memory_mb=2048,
        max_memory_entries=1024,
        max_context_tokens=200_000,
        swap_threshold_mb=1000,
        description="Maximum capability. Higher resource usage.",
    ),
}

# デフォルトプロファイル
DEFAULT_PROFILE = "lightweight"


def get_profile(name: str) -> ProfileConfig:
    """プロファイルを取得"""
    return PROFILES.get(name, PROFILES[DEFAULT_PROFILE])


def list_profiles() -> Dict[str, str]:
    """利用可能なプロファイル一覧"""
    return {k: v.description for k, v in PROFILES.items()}


def validate_profile(name: str) -> bool:
    """プロファイル名が有効か検証"""
    return name in PROFILES
