"""
Runtime Profile - Lightweight Mode Definition

Project_09: Runtime Hardening
- lightweight/balanced/full モード定義
- Mac-friendly minimal mode (default)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class RuntimeProfile(Enum):
    """Runtime profile types"""
    LIGHTWEIGHT = "lightweight"
    BALANCED = "balanced"
    FULL = "full"


@dataclass
class ProfileConfig:
    """Profile-specific configuration"""
    profile: RuntimeProfile
    embedding_enabled: bool = False
    vector_search_enabled: bool = False
    compression_enabled: bool = True
    telemetry_enabled: bool = False
    background_tasks: bool = False
    max_reflection_depth: int = 1
    max_reasoning_steps: int = 5
    max_plan_length: int = 3
    memory_cap_mb: int = 512
    token_budget: int = 50_000
    health_check_interval: int = 60
    debug: bool = False


# Profile definitions
PROFILE_CONFIGS: Dict[RuntimeProfile, ProfileConfig] = {
    RuntimeProfile.LIGHTWEIGHT: ProfileConfig(
        profile=RuntimeProfile.LIGHTWEIGHT,
        embedding_enabled=False,
        vector_search_enabled=False,
        compression_enabled=True,
        telemetry_enabled=False,
        background_tasks=False,
        max_reflection_depth=1,
        max_reasoning_steps=5,
        max_plan_length=3,
        memory_cap_mb=512,
        token_budget=50_000,
        health_check_interval=60,
        debug=False,
    ),
    RuntimeProfile.BALANCED: ProfileConfig(
        profile=RuntimeProfile.BALANCED,
        embedding_enabled=True,
        vector_search_enabled=True,
        compression_enabled=True,
        telemetry_enabled=True,
        background_tasks=False,
        max_reflection_depth=2,
        max_reasoning_steps=8,
        max_plan_length=5,
        memory_cap_mb=1024,
        token_budget=100_000,
        health_check_interval=30,
        debug=False,
    ),
    RuntimeProfile.FULL: ProfileConfig(
        profile=RuntimeProfile.FULL,
        embedding_enabled=True,
        vector_search_enabled=True,
        compression_enabled=False,
        telemetry_enabled=True,
        background_tasks=True,
        max_reflection_depth=5,
        max_reasoning_steps=15,
        max_plan_length=10,
        memory_cap_mb=2048,
        token_budget=200_000,
        health_check_interval=15,
        debug=True,
    ),
}


def get_profile(profile_name: str) -> ProfileConfig:
    """Get profile by name"""
    try:
        profile = RuntimeProfile(profile_name)
        return PROFILE_CONFIGS[profile]
    except ValueError:
        # Default to lightweight
        return PROFILE_CONFIGS[RuntimeProfile.LIGHTWEIGHT]


def get_default_profile() -> ProfileConfig:
    """Get default (lightweight) profile"""
    return PROFILE_CONFIGS[RuntimeProfile.LIGHTWEIGHT]


def is_lightweight(profile: Optional[ProfileConfig] = None) -> bool:
    """Check if profile is lightweight"""
    if profile is None:
        return True
    return profile.profile == RuntimeProfile.LIGHTWEIGHT
