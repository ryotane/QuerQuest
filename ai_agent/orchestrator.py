"""
QueryQuest Orchestrator
Manages interactions with Hermes Agent and OpenCode.
Phase 1: Loop Detection & Metric Collection
"""

import requests
import subprocess
import json
import re
from typing import List, Dict, Any, Optional
from ai_agent.utils.loop_detector import LoopDetector
from ai_agent.utils.metric_collector import MetricCollector
from ai_agent.utils.notification import notify_loop_detected, notify_error, notify_success
from ai_agent.utils.recovery import RecoveryManager
from ai_agent.utils.hard_recovery import HardRecoveryManager
# Project_039: LoopAvoidancePromptInjector連携
try:
    from ai_agent.self_improve.loop_avoidance import LoopAvoidancePromptInjector
except ImportError:
    LoopAvoidancePromptInjector = None
import logging

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.hermes_api_url = "http://localhost:8642/v1/chat/completions"
        self.hermes_api_key = ""
        self.opencode_api_url = "http://localhost:3000" # Default port, can be configured
        self.opencode_docs_url = "http://localhost:3000/doc" # OpenAPI docs
        
        # Phase 1: Monitoring components
        self.loop_detector = LoopDetector(repeat_count=3, min_length=50)
        self.metric_collector = MetricCollector()
        self.msg_id_counter = 0
        
        # Phase 2: Recovery component
        self.recovery_manager = RecoveryManager(max_retries=2)
        
        # Phase 3: Hard Recovery component
        self.hard_recovery_manager = HardRecoveryManager()
        
        # Project_039: Loop Avoidance component
        self.loop_avoidance_injector = LoopAvoidancePromptInjector() if LoopAvoidancePromptInjector else None

    def call_hermes(self, messages: List[Dict[str, str]], model: str = None, retry_count: int = 0) -> Dict[str, Any]:
        """
        Call Hermes Agent API (OpenAI-compatible).
        Phase 1: Loop Detection & Metric Collection
        Phase 2: Soft Recovery (Loop Detection)
        Phase 3: Hard Recovery
        Project_039: Loop Avoidance Prompt Injection
        """
        headers = {
            "Authorization": f"Bearer {self.hermes_api_key}",
            "Content-Type": "application/json"
        }
        
        # Project_039: ループ回避指示をシステムプロンプトに注入
        if self.loop_avoidance_injector and messages:
            for i, msg in enumerate(messages):
                if msg.get("role") == "system":
                    original_prompt = msg.get("content", "")
                    injected_prompt = self.loop_avoidance_injector.inject(original_prompt)
                    if injected_prompt != original_prompt:
                        messages[i]["content"] = injected_prompt
                    break
        
        payload = {
            "model": model or "hermes-3", # Default model, can be configured
            "messages": messages,
            "max_tokens": 4096
        }
        
        # Start metric collection
        self.metric_collector.start_session()
        
        try:
            response = requests.post(self.hermes_api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # Update token count
            if "usage" in result:
                self.metric_collector.update_token_count(result["usage"].get("total_tokens", 0))
            
            # Extract content for loop detection
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Loop detection
            self.msg_id_counter += 1
            msg_id = f"msg_{self.msg_id_counter}"
            
            # Extract thinking text if present
            thinking_text = self._extract_thinking_text(content)
            
            if thinking_text and self.loop_detector.detect(thinking_text, msg_id):
                logger.warning(f"Loop detected in message {msg_id}")
                notify_loop_detected(msg_id)
                
                # Phase 2: Soft Recovery
                new_messages = self.recovery_manager.recover(messages, msg_id)
                if new_messages is not messages:  # リカバリ適用された場合
                    logger.info(f"Soft recovery applied for msg_id: {msg_id}")
                    return self.call_hermes(new_messages, model, retry_count + 1)
                else:
                    logger.error("Max retries reached. Initiating hard recovery.")
                    # Phase 3: Hard Recovery
                    success = self.hard_recovery_manager.stop_lmstudio_generation()
                    if success:
                        return {"error": "Loop detected and max retries reached. LM Studio generation stopped."}
                    else:
                        return {"error": "Loop detected and max retries reached. Hard recovery failed."}
            
            # Success notification (only if not a retry)
            if retry_count == 0:
                notify_success("Task completed")
            
            return result
        except requests.exceptions.RequestException as e:
            notify_error(f"Hermes API error: {str(e)}")
            return {"error": f"Hermes API error: {str(e)}"}
    
    def _extract_thinking_text(self, content: str) -> str:
        """
        応答からThinkingテキストを抽出
        
        Args:
            content: 応答テキスト
            
        Returns:
            str: Thinkingテキスト
        """
        # <thinking> タグで囲まれた部分を抽出
        match = re.search(r'<thinking>(.*?)</thinking>', content, re.DOTALL)
        if match:
            return match.group(1)
        
        # "Thinking:" や "思考:" で始まる部分を抽出
        match = re.search(r'(?:Thinking|思考):\s*(.*?)(?=\n\n|$)', content, re.DOTALL)
        if match:
            return match.group(1)
        
        return ""

    def call_opencode(self, task: str, file_path: str = None) -> Dict[str, Any]:
        """
        Call OpenCode via CLI or API.
        For now, using CLI as API details are less standardized than Hermes.
        """
        if file_path:
            cmd = ["opencode", "review", file_path]
        else:
            cmd = ["opencode", "task", task]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "OpenCode command timed out"}
        except Exception as e:
            return {"error": f"OpenCode command error: {str(e)}"}

    def analyze_intent(self, user_input: str) -> str:
        """
        Simple intent analysis (can be replaced by LLM call later).
        """
        if "メモリ" in user_input or "整理" in user_input or "クリーン" in user_input:
            return "MEMORY_CLEANUP"
        elif "コード" in user_input or "レビュー" in user_input or "見て" in user_input:
            return "CODE_REVIEW"
        elif "Xcode" in user_input or "プロジェクト" in user_input:
            return "XCODE_OPEN"
        else:
            return "DIRECT_RESPONSE"

    def handle_request(self, user_input: str) -> Dict[str, Any]:
        """
        Main request handler.
        """
        intent = self.analyze_intent(user_input)
        
        if intent == "MEMORY_CLEANUP":
            # For now, just return a mock HTML response
            # In reality, this would call Hermes or a system cleanup tool
            return {
                "type": "html",
                "content": """
                <div style="padding: 20px; background: #f0f9ff; border-radius: 8px;">
                  <h3>メモリ整理完了</h3>
                  <p>2048MBの領域を解放しました。</p>
                  <p>現在のメモリ使用率: 65% (正常)</p>
                </div>
                """
            }
        elif intent == "CODE_REVIEW":
            # Call OpenCode
            result = self.call_opencode("review", "/path/to/file.swift") # Example path
            return {
                "type": "html",
                "content": f"""
                <div style="padding: 20px; border-left: 4px solid #3b82f6;">
                  <h3>コードレビュー結果</h3>
                  <pre>{result.get('stdout', 'No output')}</pre>
                </div>
                """
            }
        elif intent == "XCODE_OPEN":
            # Call AppleScript to open Xcode
            try:
                subprocess.run(["osascript", "-e", 'tell application "Xcode" to activate'], check=True)
                return {
                    "type": "html",
                    "content": """
                    <div style="padding: 20px; background: #f0fdf4; border-radius: 8px;">
                      <h3>Xcode を起動しました</h3>
                      <p>プロジェクトを開いてください。</p>
                    </div>
                    """
                }
            except Exception as e:
                return {
                    "type": "html",
                    "content": f"""
                    <div style="padding: 20px; background: #fef2f2; border-radius: 8px;">
                      <h3>Xcode 起動エラー</h3>
                      <p>{str(e)}</p>
                    </div>
                    """
                }
        else:
            # Direct response (call Hermes for general chat)
            messages = [{"role": "user", "content": user_input}]
            hermes_response = self.call_hermes(messages)
            
            if "error" in hermes_response:
                return {
                    "type": "text",
                    "content": f"エラーが発生しました: {hermes_response['error']}"
                }
            else:
                # Extract response from Hermes
                content = hermes_response.get("choices", [{}])[0].get("message", {}).get("content", "応答がありません")
                return {
                    "type": "text",
                    "content": content
                }
