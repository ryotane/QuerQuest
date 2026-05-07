# ai_agent/workspace/reflection.py

"""
自己評価（Reflection）モジュール

タスク完了後の自己レビューと、動的再プランニングを行う。
"""

import re
from datetime import datetime
from ai_agent.llm.lmstudio import LMStudioClient


llm = LMStudioClient()


def evaluate_task(task: str, output: str, context: str = "") -> dict:
    """
    タスクの実行結果を自己評価
    
    LLM に自己レビューを依頼し、スコアと改善点を取得。
    
    Args:
        task: 実行したタスク
        output: 出力結果
        context: 文脈情報
    
    Returns:
        評価結果 {
            "score": int (0-10),
            "improvements": list[str],
            "lessons": list[str],
            "retry_needed": bool
        }
    """
    try:
        prompt = f"""
以下のタスクの実行結果を自己評価してください。

【タスク】
{task[:1000]}

【出力結果】
{output[:2000]}

【文脈】
{context[:500] if context else "なし"}

【評価基準】
- 10 点: 完璧。要件を完全に満たし、品質も高い
- 7-9 点: 良好。若干の改善余地あり
- 4-6 点: 改善必要。いくつかの問題点がある
- 1-3 点: 重大な問題。再実行が必要

【出力形式】
スコア: <0-10 の整数>
改善点:
- <改善点 1>
- <改善点 2>
教訓:
- <教訓 1>
- <教訓 2>
再実行必要: <YES/NO>

スコア、改善点、教訓、再実行必要のみを出力してください。
"""
        
        result = llm.chat([
            {"role": "user", "content": prompt}
        ])
        
        # 結果をパース
        evaluation = {
            "score": 5,  # デフォルト
            "improvements": [],
            "lessons": [],
            "retry_needed": False,
            "raw_output": result
        }
        
        # スコア抽出
        score_match = re.search(r"スコア:\s*(\d+)", result, re.IGNORECASE)
        if score_match:
            evaluation["score"] = int(score_match.group(1))
        
        # 改善点抽出
        improvements_section = re.search(r"改善点:\s*(.+?)(?=教訓|$)", result, re.IGNORECASE | re.DOTALL)
        if improvements_section:
            for line in improvements_section.group(1).split('\n'):
                line = line.strip().lstrip('-•').strip()
                if line:
                    evaluation["improvements"].append(line)
        
        # 教訓抽出
        lessons_section = re.search(r"教訓:\s*(.+?)(?=再実行|$)", result, re.IGNORECASE | re.DOTALL)
        if lessons_section:
            for line in lessons_section.group(1).split('\n'):
                line = line.strip().lstrip('-•').strip()
                if line:
                    evaluation["lessons"].append(line)
        
        # 再実行必要抽出
        retry_match = re.search(r"再実行必要:\s*(\w+)", result, re.IGNORECASE)
        if retry_match:
            evaluation["retry_needed"] = retry_match.group(1).upper() == "YES"
        
        return evaluation
    
    except Exception as e:
        print(f"❌ 自己評価エラー: {e}")
        return {
            "score": 5,
            "improvements": [],
            "lessons": [],
            "retry_needed": False,
            "raw_output": str(e)
        }


def generate_retry_plan(task: str, evaluation: dict) -> dict:
    """
    再実行プランを生成
    
    Args:
        task: 元のタスク
        evaluation: 自己評価結果
    
    Returns:
        再実行プラン {
            "plan": str,
            "priority": str,
            "estimated_steps": int
        }
    """
    try:
        prompt = f"""
以下のタスクの再実行プランを生成してください。

【元のタスク】
{task[:1000]}

【自己評価結果】
スコア: {evaluation['score']}/10
改善点: {', '.join(evaluation['improvements'][:3])}
教訓: {', '.join(evaluation['lessons'][:3])}

【出力形式】
プラン: <再実行の具体的なプラン>
優先度: <high/medium/low>
推定ステップ数: <整数>

プラン、優先度、推定ステップ数のみ出力してください。
"""
        
        result = llm.chat([
            {"role": "user", "content": prompt}
        ])
        
        plan = {
            "plan": "",
            "priority": "medium",
            "estimated_steps": 3
        }
        
        # プラン抽出
        plan_match = re.search(r"プラン:\s*(.+)", result, re.IGNORECASE | re.DOTALL)
        if plan_match:
            plan["plan"] = plan_match.group(1).strip()[:500]
        
        # 優先度抽出
        priority_match = re.search(r"優先度:\s*(\w+)", result, re.IGNORECASE)
        if priority_match:
            plan["priority"] = priority_match.group(1).lower()
        
        # 推定ステップ数抽出
        steps_match = re.search(r"推定ステップ数:\s*(\d+)", result, re.IGNORECASE)
        if steps_match:
            plan["estimated_steps"] = int(steps_match.group(1))
        
        return plan
    
    except Exception as e:
        print(f"❌ 再実行プラン生成エラー: {e}")
        return {
            "plan": f"改善点: {', '.join(evaluation['improvements'][:3])}",
            "priority": "high",
            "estimated_steps": 3
        }


def check_resource_usage() -> dict:
    """
    リソース使用状況をチェック
    
    Returns:
        リソース使用状況 {
            "memory_usage_mb": float,
            "is_critical": bool,
            "recommendation": str
        }
    """
    import psutil
    import os
    
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # 閾値: 2GB 以上で警告
        is_critical = memory_mb > 2048
        
        recommendation = "正常"
        if is_critical:
            recommendation = "メモリ使用量が閾値を超えています。コンテキストを切り詰めることを検討してください。"
        elif memory_mb > 1024:
            recommendation = "メモリ使用量が上昇傾向です。注意してください。"
        
        return {
            "memory_usage_mb": round(memory_mb, 2),
            "is_critical": is_critical,
            "recommendation": recommendation
        }
    
    except ImportError:
        # psutil がない場合は簡易チェック
        return {
            "memory_usage_mb": 0,
            "is_critical": False,
            "recommendation": "psutil がインストールされていません。簡易チェックのみ。"
        }
    except Exception as e:
        return {
            "memory_usage_mb": 0,
            "is_critical": False,
            "recommendation": f"リソースチェックエラー: {e}"
        }
