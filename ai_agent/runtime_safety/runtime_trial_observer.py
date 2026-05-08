"""
Project_08: Long Runtime Trial Observer

新機能追加禁止。runtime observationのみ。
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agent.runtime_safety.safety_guard import CollapsePreventionLayer
from ai_agent.workspace.session_registry import SessionRegistry
from ai_agent.workspace.registry import WorkspaceRegistry


def observe_collapse_prevention():
    """CollapsePreventionLayerの状態観察"""
    print("=== CollapsePreventionLayer Observation ===")
    
    layer = CollapsePreventionLayer(debug=False)
    layer.plan_start_time = time.time()
    layer.plan_step_count = 5
    
    status = layer.get_status()
    print(f"  plan_ttl_remaining: {status['plan_ttl_remaining']:.1f}s")
    print(f"  plan_steps_remaining: {status['plan_steps_remaining']}")
    print(f"  total_execution_transitions: {status['total_execution_transitions']}")
    print(f"  total_plan_compressions: {status['total_plan_compressions']}")
    print(f"  total_meta_blocks: {status['total_meta_blocks']}")
    print()


def observe_session_registry():
    """SessionRegistryの状態観察"""
    print("=== SessionRegistry Observation ===")
    
    registry = SessionRegistry()
    sessions = registry.get_recent_sessions(limit=5)
    
    print(f"  total_sessions: {len(registry.data.get('sessions', []))}")
    print(f"  recent_sessions: {len(sessions)}")
    
    for i, session in enumerate(sessions[:3]):
        next_actions = session.get("next_actions", [])
        print(f"  session[{i}]: {session.get('title', 'N/A')}")
        print(f"    next_actions: {len(next_actions)} (next-action-only enforced)")
    print()


def observe_workspace_registry():
    """WorkspaceRegistryの状態観察"""
    print("=== WorkspaceRegistry Observation ===")
    
    registry = WorkspaceRegistry()
    context = registry.get_context()
    
    print(f"  workspace_id: {registry.registry.get('workspace_id', 'N/A')}")
    print(f"  active_goals: {len(registry.registry.get('active_goals', []))} (plan compression applied)")
    print(f"  recent_topics: {len(registry.registry.get('recent_topics', []))}")
    print(f"  context_length: {len(context)} chars")
    print()


def observe_memory_growth():
    """メモリ成長観察"""
    print("=== Memory Growth Observation ===")
    
    # ファイルサイズ確認
    files = [
        "memory.db",
        "memory.index",
        "memory_store.json",
        "session_registry.json",
        "workspace_registry.json",
        "project_master.json",
    ]
    
    total_size = 0
    for f in files:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f)
        if os.path.exists(path):
            size = os.path.getsize(path)
            total_size += size
            print(f"  {f}: {size / 1024:.1f} KB")
    
    print(f"  total_memory_files: {total_size / 1024:.1f} KB")
    print()


def observe_runtime_stability():
    """ランタイム安定性観察"""
    print("=== Runtime Stability Observation ===")
    
    # 簡易的なCPU/メモリチェック
    import subprocess
    
    try:
        result = subprocess.run(
            ["ps", "-o", "rss,%cpu", "-p", "1892"],  # QueryQuest API PID
            capture_output=True,
            text=True,
            timeout=5
        )
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            parts = lines[-1].split()
            rss_mb = int(parts[0]) / 1024
            cpu = float(parts[1])
            print(f"  QueryQuest API: {rss_mb:.1f} MB, {cpu}% CPU")
    except Exception as e:
        print(f"  observation failed: {e}")
    print()


if __name__ == "__main__":
    print("\n=== Project_08 Long Runtime Trial Observer ===\n")
    
    observe_collapse_prevention()
    observe_session_registry()
    observe_workspace_registry()
    observe_memory_growth()
    observe_runtime_stability()
    
    print("=== Observation Completed ===")
