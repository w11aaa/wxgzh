from datetime import datetime
import hashlib

import feedparser
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.source import Source
from app.services.classifier import classify_text
from app.services.summarizer import summarize


def _title_hash(title: str) -> str:
    return hashlib.sha256(title.strip().lower().encode('utf-8')).hexdigest()


def crawl_rss_source(db: Session, source: Source) -> int:
    feed = feedparser.parse(source.url)
    created_count = 0

    for entry in feed.entries:
        article_url = entry.get('link')
        title = (entry.get('title') or '').strip()
        if not article_url or not title:
            continue

        exists = db.query(Article).filter(Article.url == article_url).first()
        if exists:
            continue

        content = ''
        if entry.get('summary'):
            content = entry.get('summary')

        article = Article(
            source_id=source.id,
            title=title,
            url=article_url,
            author=entry.get('author'),
            content=content,
            published_at=datetime.utcnow(),
            title_hash=_title_hash(title),
            category=classify_text(f'{title} {content}'),
            summary_short=summarize(content or title),
            summary_long=summarize(content or title, max_chars=500),
        )
        db.add(article)
        created_count += 1

    db.commit()
    return created_count
