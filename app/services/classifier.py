KEYWORD_CATEGORIES: dict[str, list[str]] = {
    'ai': ['ai', '大模型', 'llm', '机器学习'],
    'backend': ['fastapi', 'python', '数据库', 'redis', 'postgresql'],
    'weixin': ['微信', '公众号', 'wechat'],
}


def classify_text(text: str) -> str:
    lowered = text.lower()
    for category, keywords in KEYWORD_CATEGORIES.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            return category
    return 'general'
