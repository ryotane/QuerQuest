# ai_agent/workspace/intent.py

"""
意図認識モジュール

ユーザーの入力から意図を検出する。
"""

# 継続意図キーワード
CONTINUITY_KEYWORDS = [
    "続き", "継続", "resume", "continue",
    "前の話", "あの話", "先ほど", "before",
    "このプロジェクト", "この作業", "this task",
    "また", "もう一度", "再開"
]

# セッション検索キーワード
SESSION_SEARCH_KEYWORDS = [
    "あのチャット", "前のチャット", "その会話",
    "chat", "session", "スレッド"
]

# 複数セッション結合キーワード
MULTI_SESSION_KEYWORDS = [
    "踏まえて", "合わせて", "結合", "マージ",
    "両方", "二つ", "複数", "cross",
    "A と B", "1 と 2"
]

# 検索キーワード抽出パターン
SEARCH_PATTERNS = [
    r"(.+?)について話した",
    r"(.+?)のチャット",
    r"(.+?)のセッション",
    r"(.+?)を探して",
    r"(.+?)を検索",
]


def detect_continuity_intent(query: str) -> bool:
    """継続意図を検出"""
    q = query.lower()
    return any(k in q for k in CONTINUITY_KEYWORDS)


def detect_session_search_intent(query: str) -> bool:
    """セッション検索意図を検出"""
    q = query.lower()
    return any(k in q for k in SESSION_SEARCH_KEYWORDS)


def detect_multi_session_intent(query: str) -> bool:
    """複数セッション結合意図を検出"""
    q = query.lower()
    return any(k in q for k in MULTI_SESSION_KEYWORDS)


def extract_search_keywords(query: str) -> list:
    """検索キーワードを抽出"""
    import re
    
    keywords = []
    for pattern in SEARCH_PATTERNS:
        match = re.search(pattern, query)
        if match:
            keyword = match.group(1).strip()
            if keyword:
                keywords.append(keyword)
    
    return keywords


def extract_session_keyword(query: str) -> str:
    """セッション検索からキーワードを抽出"""
    # 「あのチャット」の次に来る可能性のあるパターン
    patterns = [
        r"あのチャット(.+?)の",
        r"前のチャット(.+?)の",
        r"その会話(.+?)の",
        r"chat(.+?)の",
        r"session(.+?)の",
    ]
    
    import re
    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            return match.group(1).strip()
    
    return ""


def analyze_intent(query: str) -> dict:
    """
    ユーザー入力の意図を分析
    
    Returns:
        {
            "type": "continuity" | "session_search" | "multi_session" | "normal",
            "keyword": str,
            "keywords": list,
            "confidence": float
        }
    """
    q = query.lower()
    
    # 継続意図
    if detect_continuity_intent(q):
        return {
            "type": "continuity",
            "keyword": extract_session_keyword(query),
            "keywords": extract_search_keywords(query),
            "confidence": 0.8
        }
    
    # 複数セッション結合意図
    if detect_multi_session_intent(q):
        return {
            "type": "multi_session",
            "keyword": extract_session_keyword(query),
            "keywords": extract_search_keywords(query),
            "confidence": 0.7
        }
    
    # セッション検索意図
    if detect_session_search_intent(q):
        return {
            "type": "session_search",
            "keyword": extract_session_keyword(query),
            "keywords": extract_search_keywords(query),
            "confidence": 0.7
        }
    
    return {
        "type": "normal",
        "keyword": "",
        "keywords": [],
        "confidence": 0.0
    }
