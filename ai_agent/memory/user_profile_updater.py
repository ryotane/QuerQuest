"""
user_profile_updater.py - ユーザープロファイル自動更新

Project_042: ユーザープロファイルの強化
チャット履歴からユーザーの好みを抽出し、プロファイルを自動更新する。
"""

import re
from typing import Dict, List, Any, Optional
from collections import Counter
from ai_agent.memory.user_profile import get_user_profile_store, UserProfile


class UserProfileUpdater:
    """
    ユーザープロファイル自動更新クラス

    チャット履歴を分析し、ユーザーの好みや行動パターンを抽出して
    UserProfileStore に反映する。
    """

    def __init__(self):
        self.store = get_user_profile_store()

    def analyze_and_update(self, user_id: str, messages: List[Dict[str, Any]]) -> UserProfile:
        """
        メッセージ履歴を分析してプロファイルを自動更新

        Args:
            user_id: ユーザーID
            messages: メッセージリスト [{"role": "user"|"assistant", "content": "..."}, ...]

        Returns:
            更新された UserProfile
        """
        profile = self.store.get(user_id)
        if not profile:
            profile = self.store.create_or_update(user_id=user_id)

        # 分析結果をマージ
        preferences = self._analyze_preferences(messages)
        behavior_patterns = self._analyze_behavior_patterns(messages)
        context = self._analyze_context(messages)
        technical_stack = self._analyze_technical_stack(messages)
        project_history = self._analyze_project_history(messages)
        skill_level = self._analyze_skill_level(messages)
        learning_goals = self._analyze_learning_goals(messages)
        communication_style = self._analyze_communication_style(messages)

        # プロファイルを更新
        if preferences:
            profile.preferences.update(preferences)
        if behavior_patterns:
            profile.behavior_patterns.update(behavior_patterns)
        if context:
            profile.context.update(context)
        if technical_stack:
            profile.technical_stack.update(technical_stack)
        if project_history:
            # 既存の履歴とマージ（重複除去）
            existing_projects = {p.get('name') for p in profile.project_history}
            for proj in project_history:
                if proj.get('name') not in existing_projects:
                    profile.project_history.append(proj)
                    existing_projects.add(proj.get('name'))
                else:
                    # 既存の履歴を更新（頻度、期間など）
                    for existing_proj in profile.project_history:
                        if existing_proj.get('name') == proj.get('name'):
                            existing_proj.update(proj)
                            break

        # 明示的なフィードバックの適用
        feedback_prefs = self._apply_feedback(messages)
        if feedback_prefs:
            profile.preferences.update(feedback_prefs)

        # 新しいフィールドの適用
        if skill_level:
            profile.skill_level = skill_level
        if learning_goals:
            # 既存の学習目標とマージ
            existing_goals = set(profile.learning_goals)
            for goal in learning_goals:
                if goal not in existing_goals:
                    profile.learning_goals.append(goal)
                    existing_goals.add(goal)
        if communication_style:
            profile.communication_style = communication_style

        self.store.save(profile)
        return profile
    
    def update_memory(self, user_id: str, memory_os) -> int:
        """
        プロファイルを更新し、関連メモリも更新
        
        Args:
            user_id: ユーザーID
            memory_os: MemoryOSインスタンス
            
        Returns:
            更新されたエントリ数
        """
        profile = self.store.get(user_id)
        if not profile:
            return 0
        
        if memory_os and hasattr(memory_os, 'update_profile'):
            return memory_os.update_profile(
                user_id,
                profile.preferences,
                profile.behavior_patterns
            )
        return 0

    def _analyze_preferences(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        ユーザーの好みを分析

        抽出項目:
        - language: 使用言語 (ja, en, etc.)
        - tone: 会話のトーン (formal, casual, technical, etc.)
        - interests: 興味分野 (キーワード抽出)
        - code_style: コードスタイル (インデント、引用符、型ヒントなど)
        - doc_preference: ドキュメントの好み (日本語/英語、詳細度)
        - verbosity: 応答の冗長性 (concise, detailed)
        """
        preferences = {}

        # ユーザーメッセージのみを対象
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return preferences

        # 言語検出 (簡易: 日本語文字が含まれていれば ja と判定)
        japanese_chars = sum(1 for m in user_messages for c in m.get("content", "") if '\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff')
        total_chars = sum(len(m.get("content", "")) for m in user_messages)
        if total_chars > 0 and japanese_chars / total_chars > 0.3:
            preferences["language"] = "ja"
        else:
            preferences["language"] = "en"

        # トーン分析 (簡易: 敬語があれば formal, なければ casual)
        polite_count = sum(1 for m in user_messages if "です" in m.get("content", "") or "ます" in m.get("content", ""))
        if polite_count > len(user_messages) * 0.5:
            preferences["tone"] = "formal"
        else:
            preferences["tone"] = "casual"

        # 興味分野抽出 (キーワード頻出)
        interests = self._extract_interests(user_messages)
        if interests:
            preferences["interests"] = interests[:10]  # 上位10件

        # コードスタイルの分析
        code_style = self._analyze_code_style(user_messages)
        if code_style:
            preferences["code_style"] = code_style

        # ドキュメントの好み
        doc_pref = self._analyze_doc_preference(user_messages)
        if doc_pref:
            preferences["doc_preference"] = doc_pref

        # 応答の冗長性
        verbosity = self._analyze_verbosity(user_messages)
        if verbosity:
            preferences["verbosity"] = verbosity

        return preferences

    def _analyze_behavior_patterns(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        行動パターンを分析

        抽出項目:
        - frequent_commands: 頻出コマンド/キーワード
        - common_questions: よくある質問パターン
        - peak_hours: アクティブな時間帯 (簡易)
        """
        patterns = {}

        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return patterns

        # 頻出コマンド/キーワード抽出
        keywords = self._extract_keywords(user_messages)
        if keywords:
            patterns["frequent_keywords"] = keywords[:5]  # 上位5件

        # 質問パターンの検出
        questions = [m.get("content", "") for m in user_messages if "?" in m.get("content", "") or "？" in m.get("content", "")]
        if questions:
            patterns["question_count"] = len(questions)

        # 時間帯分析 (簡易: メッセージの時刻から)
        hours = []
        for m in messages:
            if "timestamp" in m:
                try:
                    hour = m["timestamp"].hour if hasattr(m["timestamp"], "hour") else None
                    if hour is not None:
                        hours.append(hour)
                except (ValueError, AttributeError):
                    pass
        if hours:
            peak_hour = Counter(hours).most_common(1)[0][0]
            patterns["peak_hour"] = peak_hour

        return patterns

    def _analyze_context(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        文脈を分析

        抽出項目:
        - recent_topics: 直近の話題
        - project_info: プロジェクト情報 (ファイル名、パスなど)
        """
        context = {}

        # 直近の話題 (最後の数メッセージからキーワード抽出)
        recent_messages = messages[-5:]  # 直近5件
        recent_keywords = self._extract_keywords(recent_messages)
        if recent_keywords:
            context["recent_topics"] = recent_keywords[:5]

        # プロジェクト情報抽出 (ファイルパス、コマンドなど)
        project_info = self._extract_project_info(messages)
        if project_info:
            context["project_info"] = project_info

        return context

    def _analyze_code_style(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        コードスタイルを分析

        抽出項目:
        - indent_style: インデントスタイル (space, tab)
        - quote_style: 引用符のスタイル (single, double)
        - type_hints: 型ヒントの使用 (yes, no)
        """
        style = {}
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return style

        # コードブロックの抽出
        code_blocks = []
        for m in user_messages:
            content = m.get("content", "")
            # Markdown コードブロックの抽出
            blocks = re.findall(r'```(?:\w+)?\n(.*?)```', content, re.DOTALL)
            code_blocks.extend(blocks)

        if not code_blocks:
            return style

        # インデントスタイルの分析
        indent_counts = {'space': 0, 'tab': 0}
        for block in code_blocks:
            lines = block.split('\n')
            for line in lines:
                if line.startswith(' '):
                    indent_counts['space'] += 1
                elif line.startswith('\t'):
                    indent_counts['tab'] += 1
        
        if indent_counts['space'] > indent_counts['tab']:
            style['indent_style'] = 'space'
        elif indent_counts['tab'] > indent_counts['space']:
            style['indent_style'] = 'tab'

        # 引用符のスタイルの分析
        quote_counts = {'single': 0, 'double': 0}
        for block in code_blocks:
            quote_counts['single'] += block.count("'")
            quote_counts['double'] += block.count('"')
        
        if quote_counts['single'] > quote_counts['double']:
            style['quote_style'] = 'single'
        elif quote_counts['double'] > quote_counts['single']:
            style['quote_style'] = 'double'

        # 型ヒントの使用
        type_hint_patterns = [': int', ': str', ': float', ': bool', ': List', ': Dict', ': Optional']
        has_type_hints = any(pattern in ''.join(code_blocks) for pattern in type_hint_patterns)
        style['type_hints'] = 'yes' if has_type_hints else 'no'

        return style

    def _analyze_doc_preference(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        ドキュメントの好みを分析

        抽出項目:
        - language: ドキュメントの言語 (ja, en)
        - detail_level: 詳細度 (concise, detailed)
        """
        pref = {}
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return pref

        # ドキュメント関連のキーワード
        doc_keywords_ja = ['ドキュメント', '説明', '仕様', 'マニュアル', 'README']
        doc_keywords_en = ['document', 'description', 'specification', 'manual', 'readme']
        
        ja_count = sum(sum(1 for kw in doc_keywords_ja if kw in m.get("content", "")) for m in user_messages)
        en_count = sum(sum(1 for kw in doc_keywords_en if kw in m.get("content", "")) for m in user_messages)
        
        if ja_count > en_count:
            pref['language'] = 'ja'
        else:
            pref['language'] = 'en'

        # 詳細度の分析 (キーワードとメッセージの長さから推測)
        detailed_keywords = ['詳しく', '詳細に', '説明して', 'explain', 'detail', 'comprehensive']
        concise_keywords = ['簡潔に', '簡単に', '要約して', 'short', 'brief', 'concise']
        
        detailed_count = sum(sum(1 for kw in detailed_keywords if kw in m.get("content", "")) for m in user_messages)
        concise_count = sum(sum(1 for kw in concise_keywords if kw in m.get("content", "")) for m in user_messages)
        
        if detailed_count > concise_count:
            pref['detail_level'] = 'detailed'
        elif concise_count > detailed_count:
            pref['detail_level'] = 'concise'
        else:
            # キーワードがない場合はメッセージの長さで判定
            avg_length = sum(len(m.get("content", "")) for m in user_messages) / len(user_messages)
            pref['detail_level'] = 'detailed' if avg_length > 100 else 'concise'

        return pref

    def _analyze_verbosity(self, messages: List[Dict[str, Any]]) -> str:
        """
        応答の冗長性を分析

        抽出項目:
        - verbosity: 冗長性 (concise, detailed)
        """
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return "concise"

        # 簡潔さを求めるキーワード
        concise_keywords = ['簡潔に', '簡単に', '要約して', 'short', 'brief', 'concise']
        # 詳細さを求めるキーワード
        detailed_keywords = ['詳しく', '詳細に', '説明して', 'explain', 'detail', 'comprehensive']
        
        concise_count = sum(sum(1 for kw in concise_keywords if kw in m.get("content", "")) for m in user_messages)
        detailed_count = sum(sum(1 for kw in detailed_keywords if kw in m.get("content", "")) for m in user_messages)
        
        if detailed_count > concise_count:
            return "detailed"
        else:
            return "concise"

    def _analyze_technical_stack(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        技術スタックを分析

        抽出項目:
        - frameworks: 使用されているフレームワーク (例: React, Django, FastAPI)
        - languages: 使用されているプログラミング言語 (例: Python, JavaScript)
        - tools: 使用されているツール (例: Docker, Git, Kubernetes)
        - databases: 使用されているデータベース (例: PostgreSQL, MongoDB)
        """
        stack = {}
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return stack

        # 技術用語リストの拡張
        known_frameworks = [
            "React", "Vue", "Angular", "Django", "Flask", "FastAPI", "Express", 
            "Next.js", "Nuxt", "Spring", "Laravel", "Rails", "Svelte", "SolidJS",
            "Tailwind", "Bootstrap", "jQuery", "Node.js", "Electron", "Flutter",
            "React Native", "PyTorch", "TensorFlow", "Scikit-learn", "Pandas", "NumPy"
        ]
        known_languages = [
            "Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++", "C#", 
            "Ruby", "PHP", "Swift", "Kotlin", "Scala", "Elixir", "Erlang", "Haskell",
            "Lua", "Julia", "Dart", "Shell", "Bash", "SQL", "HTML", "CSS"
        ]
        known_tools = [
            "Docker", "Kubernetes", "Git", "AWS", "Azure", "GCP", "Terraform", 
            "Ansible", "Jenkins", "GitHub Actions", "Vercel", "Netlify", "Heroku",
            "Postman", "Webpack", "Vite", "Babel", "ESLint", "Prettier", "npm", "yarn", "pip", "poetry", "cargo"
        ]
        known_databases = [
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "DynamoDB", 
            "Cassandra", "Elasticsearch", "Neo4j", "CouchDB", "Firebase", "Supabase"
        ]

        frameworks_found = []
        languages_found = []
        tools_found = []
        databases_found = []

        for m in user_messages:
            content = m.get("content", "")
            
            # コードブロックの言語指定からの検出 (例: ```typescript → TypeScript)
            lang_spec_matches = re.findall(r'```(\w+)', content)
            for lang_spec in lang_spec_matches:
                # 言語指定をknown_languagesと照合
                for lang in known_languages:
                    if lang.lower() == lang_spec.lower():
                        languages_found.append(lang)
                # フレームワーク指定もチェック
                for fw in known_frameworks:
                    if fw.lower() == lang_spec.lower():
                        frameworks_found.append(fw)

            # コードブロック内のみを検出対象にする
            code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', content, re.DOTALL)
            for code_block in code_blocks:
                # 基本マッチ
                for fw in known_frameworks:
                    if fw.lower() in code_block.lower():
                        frameworks_found.append(fw)
                for lang in known_languages:
                    if lang.lower() in code_block.lower():
                        languages_found.append(lang)
                for tool in known_tools:
                    if tool.lower() in code_block.lower():
                        tools_found.append(tool)
                for db in known_databases:
                    if db.lower() in code_block.lower():
                        databases_found.append(db)

                # インポート文やパッケージ管理コマンドからの検出 (高度なパターンマッチング)
                # Python: import pandas, from django
                if re.search(r'import\s+(pandas|numpy|django|flask|fastapi|sqlalchemy|celery|pytest|requests|boto3)', code_block):
                    frameworks_found.extend(['pandas', 'numpy', 'django', 'flask', 'fastapi', 'sqlalchemy', 'celery', 'pytest', 'requests', 'boto3'])
                # JS/TS: require('react'), import React from 'react'
                if re.search(r"(require\s*\(\s*['\"]react['\"]\)|import\s+.*\s+from\s+['\"]react['\"])", code_block):
                    frameworks_found.append('React')
                if re.search(r"(require\s*\(\s*['\"]vue['\"]\)|import\s+.*\s+from\s+['\"]vue['\"])", code_block):
                    frameworks_found.append('Vue')
                if re.search(r"(require\s*\(\s*['\"]express['\"]\)|import\s+.*\s+from\s+['\"]express['\"])", code_block):
                    frameworks_found.append('Express')
                # npm/pip install
                if re.search(r'(npm\s+install\s+|yarn\s+add\s+|pip\s+install\s+|poetry\s+add\s+)(react|vue|angular|django|flask|fastapi|express|tailwind|bootstrap)', code_block):
                    frameworks_found.extend(['react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express', 'tailwind', 'bootstrap'])

        if frameworks_found:
            stack["frameworks"] = list(set(frameworks_found))  # 重複除去
        if languages_found:
            stack["languages"] = list(set(languages_found))  # 重複除去
        if tools_found:
            stack["tools"] = list(set(tools_found))  # 重複除去
        if databases_found:
            stack["databases"] = list(set(databases_found))  # 重複除去

        return stack

    def _analyze_project_history(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        プロジェクト履歴を分析

        抽出項目:
        - name: プロジェクト名 (ファイル名、ディレクトリ名から推測)
        - description: プロジェクトの説明 (メッセージから抽出)
        - technologies: 使用技術 (技術スタックから抽出)
        - first_seen: 初回アクティビティ時刻
        - last_seen: 最終アクティビティ時刻
        - frequency: 頻度 (メッセージ数)
        """
        history = []
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return history

        # プロジェクト名の抽出と頻度・期間の追跡
        project_data = {}  # {name: {'count': int, 'first_seen': datetime, 'last_seen': datetime}}
        for m in user_messages:
            content = m.get("content", "")
            timestamp = m.get("timestamp")
            
            # ファイルパスからプロジェクト名を推測 (例: /path/to/project_name/file.py -> project_name)
            paths = re.findall(r'/([^/]+)/[^/]+\.(py|md|json|js|ts|go|rs)', content)
            for path in paths:
                name = path[0]
                if name not in project_data:
                    project_data[name] = {'count': 0, 'first_seen': timestamp, 'last_seen': timestamp}
                project_data[name]['count'] += 1
                if timestamp and (not project_data[name]['last_seen'] or timestamp > project_data[name]['last_seen']):
                    project_data[name]['last_seen'] = timestamp
                if timestamp and (not project_data[name]['first_seen'] or timestamp < project_data[name]['first_seen']):
                    project_data[name]['first_seen'] = timestamp
                    
            # ディレクトリ名の抽出 (例: cd project_name, mkdir project_name)
            dir_names = re.findall(r'(?:cd|mkdir|ls|git clone)\s+([^\s]+)', content)
            for name in dir_names:
                if name not in project_data:
                    project_data[name] = {'count': 0, 'first_seen': timestamp, 'last_seen': timestamp}
                project_data[name]['count'] += 1
                if timestamp and (not project_data[name]['last_seen'] or timestamp > project_data[name]['last_seen']):
                    project_data[name]['last_seen'] = timestamp
                if timestamp and (not project_data[name]['first_seen'] or timestamp < project_data[name]['first_seen']):
                    project_data[name]['first_seen'] = timestamp

        # 各プロジェクト名に対して、関連する技術スタックを抽出
        for name, data in project_data.items():
            tech_stack = self._analyze_technical_stack(user_messages)
            history.append({
                "name": name,
                "technologies": tech_stack,
                "description": f"プロジェクト '{name}' に関連する会話",
                "frequency": data['count'],
                "first_seen": data['first_seen'],
                "last_seen": data['last_seen']
            })

        # 頻度順にソート
        history.sort(key=lambda x: x.get('frequency', 0), reverse=True)

        return history

    def _apply_feedback(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        ユーザーの明示的なフィードバックをプロファイルに反映

        例:
        - "もっと詳しく" -> detail_level: detailed
        - "簡潔に" -> detail_level: concise
        - "英語で" -> language: en
        """
        feedback_prefs = {}
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return feedback_prefs

        # 明示的な指示の検出
        detailed_keywords = ['詳しく', '詳細に', 'もっと詳しく', '詳細な説明', 'explain in detail', 'comprehensive']
        concise_keywords = ['簡潔に', '簡単に', '要約して', 'short', 'brief', 'concise']
        ja_keywords = ['日本語で', '日本語で書いて', 'ja', 'japanese']
        en_keywords = ['英語で', '英語で書いて', 'en', 'english']

        # 直近のメッセージの重みを高くする
        recent_messages = user_messages[-3:]  # 直近3件
        older_messages = user_messages[:-3] if len(user_messages) > 3 else []

        detailed_count = sum(sum(1 for kw in detailed_keywords if kw in m.get("content", "")) for m in recent_messages) * 2
        concise_count = sum(sum(1 for kw in concise_keywords if kw in m.get("content", "")) for m in recent_messages) * 2
        ja_count = sum(sum(1 for kw in ja_keywords if kw in m.get("content", "")) for m in recent_messages) * 2
        en_count = sum(sum(1 for kw in en_keywords if kw in m.get("content", "")) for m in recent_messages) * 2

        # 古いメッセージも加算（重みは低め）
        detailed_count += sum(sum(1 for kw in detailed_keywords if kw in m.get("content", "")) for m in older_messages)
        concise_count += sum(sum(1 for kw in concise_keywords if kw in m.get("content", "")) for m in older_messages)
        ja_count += sum(sum(1 for kw in ja_keywords if kw in m.get("content", "")) for m in older_messages)
        en_count += sum(sum(1 for kw in en_keywords if kw in m.get("content", "")) for m in older_messages)

        if detailed_count > concise_count:
            feedback_prefs['detail_level'] = 'detailed'
        elif concise_count > detailed_count:
            feedback_prefs['detail_level'] = 'concise'

        if ja_count > en_count:
            feedback_prefs['language'] = 'ja'
        elif en_count > ja_count:
            feedback_prefs['language'] = 'en'

        return feedback_prefs

    def _analyze_skill_level(self, messages: List[Dict[str, Any]]) -> str:
        """
        ユーザーのスキルレベルを分析

        抽出項目:
        - skill_level: スキルレベル (beginner, intermediate, advanced)
        """
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return ""

        # スキルレベルのキーワード
        beginner_keywords = ['初心者', 'はじめ', '基本', '基礎', 'how to', 'what is', 'beginner']
        intermediate_keywords = ['中級', '応用', '実践', 'intermediate', 'advanced', 'expert']
        advanced_keywords = ['上級', '高度', '最適化', 'パフォーマンス', 'advanced', 'expert', 'senior']

        beginner_count = sum(sum(1 for kw in beginner_keywords if kw in m.get("content", "")) for m in user_messages)
        intermediate_count = sum(sum(1 for kw in intermediate_keywords if kw in m.get("content", "")) for m in user_messages)
        advanced_count = sum(sum(1 for kw in advanced_keywords if kw in m.get("content", "")) for m in user_messages)

        if advanced_count > intermediate_count and advanced_count > beginner_count:
            return "advanced"
        elif intermediate_count > beginner_count:
            return "intermediate"
        else:
            return "beginner"

    def _analyze_learning_goals(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        ユーザーの学習目標を分析

        抽出項目:
        - learning_goals: 学習目標 (リスト)
        """
        learning_goals = []
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return learning_goals

        # 学習目標のキーワード
        goal_keywords = ['学びたい', '覚えたい', '理解したい', 'learn', 'understand', 'master', 'study']
        
        for m in user_messages:
            content = m.get("content", "")
            if any(kw in content.lower() for kw in goal_keywords):
                # 文脈から学習目標を抽出 (簡易: 直前の名詞句)
                # 実際にはより高度なNLPが必要だが、簡易実装としてキーワード周辺を抽出
                import re
                # 「〜を学びたい」の「〜」部分を抽出
                matches = re.findall(r'(.+?)を学びたい|(.+?)を覚えたい|(.+?)を理解したい', content)
                for match in matches:
                    goal = match[0] or match[1] or match[2]
                    if goal:
                        learning_goals.append(goal.strip())
                
                # 英語の場合
                en_matches = re.findall(r'want to learn (.+?)|want to understand (.+?)|want to master (.+?)', content.lower())
                for match in en_matches:
                    goal = match[0] or match[1] or match[2]
                    if goal:
                        learning_goals.append(goal.strip())

        return list(set(learning_goals))  # 重複除去

    def _analyze_communication_style(self, messages: List[Dict[str, Any]]) -> str:
        """
        ユーザーのコミュニケーションスタイルを分析

        抽出項目:
        - communication_style: コミュニケーションスタイル (direct, explanatory, Socratic)
        """
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return ""

        # コミュニケーションスタイルのキーワード
        direct_keywords = ['教えて', '書いて', '作って', 'show me', 'give me', 'create']
        explanatory_keywords = ['説明して', 'なぜ', 'どうして', 'explain', 'why', 'how does', 'tell me']
        socratic_keywords = ['どう思う', '意見', 'アドバイス', 'opinion', 'advice', 'suggest']

        direct_count = sum(sum(1 for kw in direct_keywords if kw in m.get("content", "")) for m in user_messages)
        explanatory_count = sum(sum(1 for kw in explanatory_keywords if kw in m.get("content", "")) for m in user_messages)
        socratic_count = sum(sum(1 for kw in socratic_keywords if kw in m.get("content", "")) for m in user_messages)

        if explanatory_count > direct_count and explanatory_count > socratic_count:
            return "explanatory"
        elif socratic_count > direct_count:
            return "Socratic"
        else:
            return "direct"

    def _extract_interests(self, messages: List[Dict[str, Any]]) -> List[str]:
        """興味分野を抽出 (簡易: 頻出単語)"""
        # 実装: 専門用語や技術用語の頻出を分析
        # 現在はキーワード抽出を流用
        return self._extract_keywords(messages)

    def _extract_keywords(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        メッセージからキーワードを抽出

        実装: 名詞や技術用語を頻出順に抽出
        """
        # 簡易実装: 空白区切りの単語をカウント
        word_counts = Counter()
        for m in messages:
            content = m.get("content", "")
            # 日本語は文字単位、英語は単語単位で分割
            words = re.findall(r'\b\w+\b', content)
            word_counts.update(words)

        # 頻出順に返す (ストップワードは除く)
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                      "have", "has", "had", "do", "does", "did", "will", "would", "could",
                      "should", "may", "might", "can", "shall", "to", "of", "in", "for",
                      "on", "with", "at", "by", "from", "as", "into", "through", "during",
                      "before", "after", "above", "below", "between", "out", "off", "over",
                      "under", "again", "further", "then", "once", "here", "there", "when",
                      "where", "why", "how", "all", "both", "each", "few", "more", "most",
                      "other", "some", "such", "no", "nor", "not", "only", "own", "same",
                      "so", "than", "too", "very", "s", "t", "just", "don", "now", "also"}

        filtered_words = [word for word, count in word_counts.most_common(20)
                          if word.lower() not in stop_words and len(word) > 2]

        return filtered_words

    def _extract_project_info(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """プロジェクト情報を抽出 (ファイルパス、コマンドなど)"""
        info = {}

        # ファイルパスの抽出
        file_paths = set()
        for m in messages:
            content = m.get("content", "")
            # ファイルパスのパターン (例: /path/to/file, ./file, file.py)
            paths = re.findall(r'[\w./\-]+\.py|[\w./\-]+\.md|[\w./\-]+\.json', content)
            file_paths.update(paths)

        if file_paths:
            info["files"] = list(file_paths)[:10]  # 上位10件

        # コマンドの抽出
        commands = set()
        for m in messages:
            content = m.get("content", "")
            # コマンドのパターン (例: $ command, > command, command --flag)
            cmd_matches = re.findall(r'\$ ([^\n]+)|> ([^\n]+)', content)
            for match in cmd_matches:
                cmd = match[0] or match[1]
                if cmd:
                    commands.add(cmd.strip())

        if commands:
            info["commands"] = list(commands)[:10]

        return info


# グローバルインスタンス
_updater = None


def get_updater() -> UserProfileUpdater:
    """UserProfileUpdater のインスタンスを取得"""
    global _updater
    if _updater is None:
        _updater = UserProfileUpdater()
    return _updater
