def summarize(content: str, max_chars: int = 140) -> str:
    if not content:
        return ''
    cleaned = ' '.join(content.split())
    if len(cleaned) <= max_chars:
        return cleaned
    return f'{cleaned[: max_chars - 3]}...'
